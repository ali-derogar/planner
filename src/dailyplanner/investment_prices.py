"""Fetch market prices for investment assets (TGJU + Nobitex)."""
import json
import re
import urllib.error
import urllib.request
from typing import Dict, List, Optional, Tuple

from dailyplanner.investments import asset_price_key

_FETCH_HEADERS = {
    "User-Agent": "DailyPlanner/1.0",
    "Accept": "application/json",
}
_TIMEOUT = 12

# (market, asset) -> (source, symbol)
ASSET_PRICE_SOURCES: Dict[Tuple[str, str], Tuple[str, str]] = {
    ("فیزیکی", "طلا"): ("tgju", "geram18"),
    ("فیزیکی", "نقره"): ("tgju", "silver_999"),
    ("فیزیکی", "سکه"): ("tgju", "sekee"),
    ("صندوق", "عیار"): ("tgju", "geram18"),
    ("صندوق", "نقرابی"): ("tgju", "silver_999"),
    ("رمزارز", "BTC/USDT"): ("nobitex", "BTCIRT"),
    ("رمزارز", "ETH/USDT"): ("nobitex", "ETHIRT"),
    ("رمزارز", "BNB/USDT"): ("nobitex", "BNBIRT"),
    ("رمزارز", "XRP/USDT"): ("nobitex", "XRPIRT"),
    ("رمزارز", "SOL/USDT"): ("nobitex", "SOLIRT"),
    ("رمزارز", "TON/USDT"): ("nobitex", "TONIRT"),
    ("رمزارز", "TRX/USDT"): ("nobitex", "TRXIRT"),
}

_TGJU_URL = "https://call.tgju.org/ajax.json"
_NOBITEX_URL = "https://api.nobitex.ir/market/stats"


def _parse_price(raw) -> Optional[int]:
    if raw is None:
        return None
    text = str(raw).strip().replace(",", "").replace("،", "")
    text = re.sub(r"[^\d.]", "", text)
    if not text:
        return None
    try:
        value = float(text)
    except ValueError:
        return None
    if value <= 0:
        return None
    return int(round(value))


def _fetch_json(url: str, extra_headers: Optional[dict] = None) -> dict:
    headers = dict(_FETCH_HEADERS)
    if extra_headers:
        headers.update(extra_headers)
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_tgju_prices() -> Dict[str, int]:
    data = _fetch_json(_TGJU_URL, {"Referer": "https://www.tgju.org/"})
    current = data.get("current") or {}
    out: Dict[str, int] = {}
    for symbol, payload in current.items():
        if not isinstance(payload, dict):
            continue
        price = _parse_price(payload.get("p"))
        if price:
            out[symbol] = price
    return out


def fetch_nobitex_prices() -> Dict[str, int]:
    data = _fetch_json(_NOBITEX_URL)
    stats = data.get("stats") or {}
    out: Dict[str, int] = {}
    for pair, payload in stats.items():
        if not isinstance(payload, dict):
            continue
        # Nobitex prices are in Rial; convert to Toman.
        price = _parse_price(payload.get("latest"))
        if price:
            out[pair.replace("-", "")] = max(1, price // 10)
    return out


def price_source_for_asset(market: str, asset: str) -> Optional[Tuple[str, str]]:
    return ASSET_PRICE_SOURCES.get((market.strip(), asset.strip()))


def fetch_price_for_asset(
    market: str,
    asset: str,
    tgju_cache: Optional[Dict[str, int]] = None,
    nobitex_cache: Optional[Dict[str, int]] = None,
) -> Optional[int]:
    source = price_source_for_asset(market, asset)
    if not source:
        return None
    src, symbol = source
    if src == "tgju":
        cache = tgju_cache if tgju_cache is not None else fetch_tgju_prices()
        return cache.get(symbol)
    if src == "nobitex":
        cache = nobitex_cache if nobitex_cache is not None else fetch_nobitex_prices()
        return cache.get(symbol)
    return None


def sync_prices_for_assets(
    assets: List[Tuple[str, str]],
) -> Tuple[Dict[str, int], List[str]]:
    """Return ({market|asset: price}, error_messages)."""
    unique = []
    seen = set()
    for market, asset in assets or []:
        key = (market.strip(), asset.strip())
        if not key[0] or not key[1] or key in seen:
            continue
        if not price_source_for_asset(key[0], key[1]):
            continue
        seen.add(key)
        unique.append(key)

    if not unique:
        return {}, []

    tgju_cache: Dict[str, int] = {}
    nobitex_cache: Dict[str, int] = {}
    errors: List[str] = []
    try:
        if any(price_source_for_asset(m, a)[0] == "tgju" for m, a in unique):
            tgju_cache = fetch_tgju_prices()
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
        errors.append(f"TGJU: {exc}")
    try:
        if any(price_source_for_asset(m, a)[0] == "nobitex" for m, a in unique):
            nobitex_cache = fetch_nobitex_prices()
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
        errors.append(f"Nobitex: {exc}")

    out: Dict[str, int] = {}
    for market, asset in unique:
        price = fetch_price_for_asset(market, asset, tgju_cache, nobitex_cache)
        if price and price > 0:
            out[asset_price_key(market, asset)] = price
    return out, errors
