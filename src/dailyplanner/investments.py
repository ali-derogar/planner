"""Investment taxonomy: risk level → market type → asset."""
import json
from typing import Any, Dict, List, Optional

INVESTMENT_RISKS = [
    {"value": "بدون ریسک", "label": "بدون ریسک", "emoji": "🛡️"},
    {"value": "کم ریسک", "label": "کم ریسک", "emoji": "🟢"},
    {"value": "ریسک متوسط", "label": "ریسک متوسط", "emoji": "🟡"},
    {"value": "پر ریسک", "label": "پر ریسک", "emoji": "🔴"},
]

INVESTMENT_MARKETS = [
    {"value": "فیزیکی", "label": "فیزیکی", "emoji": "🪙"},
    {"value": "بورس", "label": "بورس", "emoji": "📈"},
    {"value": "صندوق", "label": "صندوق", "emoji": "💹"},
    {"value": "سپرده بانکی", "label": "سپرده بانکی", "emoji": "🏦"},
    {"value": "املاک", "label": "املاک", "emoji": "🏠"},
    {"value": "خودرو", "label": "خودرو", "emoji": "🚗"},
    {"value": "بورس کالا", "label": "بورس کالا", "emoji": "📦"},
    {"value": "رمزارز", "label": "رمزارز", "emoji": "₿"},
]

INVESTMENT_ASSETS: Dict[str, List[Dict[str, str]]] = {
    "فیزیکی": [
        {"value": "طلا", "label": "طلا", "emoji": "🥇"},
        {"value": "نقره", "label": "نقره", "emoji": "🥈"},
        {"value": "سکه", "label": "سکه", "emoji": "🪙"},
        {"value": "جواهر", "label": "جواهر", "emoji": "💍"},
    ],
    "بورس": [
        {"value": "سهام عمومی", "label": "سهام عمومی", "emoji": "📊"},
        {"value": "فولاد", "label": "فولاد", "emoji": "🏭"},
        {"value": "خودروسازی", "label": "خودروسازی", "emoji": "🚙"},
        {"value": "بانکی", "label": "بانکی", "emoji": "🏛️"},
        {"value": "پتروشیمی", "label": "پتروشیمی", "emoji": "⚗️"},
    ],
    "صندوق": [
        {"value": "عیار", "label": "عیار", "emoji": "✨"},
        {"value": "نقرابی", "label": "نقرابی", "emoji": "🥈"},
        {"value": "کهربا", "label": "کهربا", "emoji": "🟠"},
        {"value": "آگاس", "label": "آگاس", "emoji": "🔷"},
        {"value": "درآمد ثابت", "label": "درآمد ثابت", "emoji": "💵"},
    ],
    "سپرده بانکی": [
        {"value": "کوتاه‌مدت", "label": "کوتاه‌مدت", "emoji": "📅"},
        {"value": "بلندمدت", "label": "بلندمدت", "emoji": "🗓️"},
        {"value": "گواهی سپرده", "label": "گواهی سپرده", "emoji": "📜"},
    ],
    "املاک": [
        {"value": "مسکن", "label": "مسکن", "emoji": "🏠"},
        {"value": "زمین", "label": "زمین", "emoji": "🌍"},
        {"value": "تجاری", "label": "تجاری", "emoji": "🏢"},
    ],
    "خودرو": [
        {"value": "سواری", "label": "سواری", "emoji": "🚗"},
        {"value": "کار", "label": "کار", "emoji": "🚚"},
        {"value": "موتور", "label": "موتور", "emoji": "🏍️"},
    ],
    "بورس کالا": [
        {"value": "زرین", "label": "زرین", "emoji": "🌾"},
        {"value": "پنبه", "label": "پنبه", "emoji": "☁️"},
        {"value": "سیمان", "label": "سیمان", "emoji": "🧱"},
        {"value": "فولاد کالا", "label": "فولاد کالا", "emoji": "🔩"},
    ],
    "رمزارز": [
        {"value": "BTC/USDT", "label": "BTC/USDT", "emoji": "₿"},
        {"value": "ETH/USDT", "label": "ETH/USDT", "emoji": "⟠"},
        {"value": "BNB/USDT", "label": "BNB/USDT", "emoji": "🔶"},
        {"value": "XRP/USDT", "label": "XRP/USDT", "emoji": "💧"},
        {"value": "SOL/USDT", "label": "SOL/USDT", "emoji": "◎"},
        {"value": "TON/USDT", "label": "TON/USDT", "emoji": "💎"},
        {"value": "TRX/USDT", "label": "TRX/USDT", "emoji": "🔺"},
    ],
}

INVESTMENT_RISK_MARKETS: Dict[str, List[str]] = {
    "بدون ریسک": ["سپرده بانکی", "صندوق"],
    "کم ریسک": ["فیزیکی", "صندوق"],
    "ریسک متوسط": ["بورس", "املاک", "خودرو", "بورس کالا"],
    "پر ریسک": ["بورس", "رمزارز"],
}

_LEGACY_CATEGORY_MAP = {
    "سهام": ("ریسک متوسط", "بورس", "سهام عمومی"),
    "طلا": ("کم ریسک", "فیزیکی", "طلا"),
    "رمزارز": ("پر ریسک", "رمزارز", "BTC/USDT"),
    "سپرده بانکی": ("بدون ریسک", "سپرده بانکی", "کوتاه‌مدت"),
    "صندوق": ("کم ریسک", "صندوق", "درآمد ثابت"),
    "املاک": ("ریسک متوسط", "املاک", "مسکن"),
    "سایر": ("ریسک متوسط", "بورس", "سهام عمومی"),
}


def markets_for_risk(risk: str) -> List[Dict[str, str]]:
    keys = INVESTMENT_RISK_MARKETS.get(risk.strip(), [])
    return [m for m in INVESTMENT_MARKETS if m["value"] in keys]


def is_valid_risk_market(risk: str, market: str) -> bool:
    return market.strip() in INVESTMENT_RISK_MARKETS.get(risk.strip(), [])


def get_investment_taxonomy() -> dict:
    return {
        "risks": INVESTMENT_RISKS,
        "markets": INVESTMENT_MARKETS,
        "markets_by_risk": {
            risk["value"]: markets_for_risk(risk["value"]) for risk in INVESTMENT_RISKS
        },
        "assets": INVESTMENT_ASSETS,
    }


def all_investment_asset_labels() -> List[str]:
    labels: List[str] = []
    for items in INVESTMENT_ASSETS.values():
        for item in items:
            labels.append(item["label"])
    return labels


def encode_investment_category(risk: str, market: str, asset: str) -> str:
    return json.dumps(
        {"risk": risk.strip(), "market": market.strip(), "asset": asset.strip()},
        ensure_ascii=False,
    )


def decode_investment_category(category: str) -> Optional[Dict[str, str]]:
    if not category:
        return None
    text = category.strip()
    if text.startswith("{"):
        try:
            data = json.loads(text)
            if isinstance(data, dict) and data.get("asset"):
                return {
                    "risk": str(data.get("risk") or ""),
                    "market": str(data.get("market") or ""),
                    "asset": str(data.get("asset") or ""),
                }
        except (json.JSONDecodeError, TypeError):
            return None
    if text in _LEGACY_CATEGORY_MAP:
        risk, market, asset = _LEGACY_CATEGORY_MAP[text]
        return {"risk": risk, "market": market, "asset": asset}
    return {"risk": "", "market": "", "asset": text}


def _emoji_for(items: List[Dict[str, str]], value: str, fallback: str = "💎") -> str:
    for item in items:
        if item.get("value") == value or item.get("label") == value:
            return item.get("emoji") or fallback
    return fallback


def investment_meta_dict(meta: Optional[Dict[str, str]]) -> Dict[str, Any]:
    if not meta:
        return {}
    risk = meta.get("risk") or ""
    market = meta.get("market") or ""
    asset = meta.get("asset") or ""
    risk_emoji = _emoji_for(INVESTMENT_RISKS, risk, "📊")
    market_emoji = _emoji_for(INVESTMENT_MARKETS, market, "💼")
    asset_emoji = _emoji_for(INVESTMENT_ASSETS.get(market, []), asset, "💎")
    parts = []
    if asset:
        parts.append(f"{asset_emoji} {asset}")
    if market:
        parts.append(f"{market_emoji} {market}")
    if risk:
        parts.append(f"{risk_emoji} {risk}")
    return {
        "risk": risk,
        "market": market,
        "asset": asset,
        "risk_emoji": risk_emoji,
        "market_emoji": market_emoji,
        "asset_emoji": asset_emoji,
        "display": " · ".join(parts),
        "group_key": asset or market or risk,
    }


def investment_group_key(category: str) -> str:
    meta = decode_investment_category(category)
    if not meta:
        return category or "سایر"
    return meta.get("asset") or meta.get("market") or category or "سایر"


def merge_custom_assets(taxonomy: dict, custom_assets: List[Dict[str, str]]) -> dict:
    assets = {k: list(v) for k, v in taxonomy.get("assets", {}).items()}
    for item in custom_assets or []:
        market = str(item.get("market") or "").strip()
        value = str(item.get("value") or item.get("label") or "").strip()
        if not market or not value:
            continue
        if market not in assets:
            assets[market] = []
        if any(a.get("value") == value for a in assets[market]):
            continue
        assets[market].append({
            "value": value,
            "label": str(item.get("label") or value),
            "emoji": str(item.get("emoji") or "💎"),
        })
    return {
        **taxonomy,
        "assets": assets,
    }


def investment_pnl_percent(
    unit_price: Optional[int], current_unit_price: Optional[int]
) -> Optional[float]:
    if not unit_price or not current_unit_price or unit_price <= 0:
        return None
    return round((current_unit_price - unit_price) / unit_price * 100, 2)


def portfolio_breakdown(entries) -> Dict[str, Dict[str, int]]:
    by_asset: Dict[str, int] = {}
    by_risk: Dict[str, int] = {}
    for entry in entries:
        signed = entry.signed_amount if hasattr(entry, "signed_amount") else entry.amount
        if not signed:
            continue
        key = investment_group_key(entry.category or "")
        by_asset[key] = by_asset.get(key, 0) + signed
        meta = decode_investment_category(entry.category or "") or {}
        risk = meta.get("risk") or "سایر"
        by_risk[risk] = by_risk.get(risk, 0) + signed
    return {"by_asset": by_asset, "by_risk": by_risk}


def asset_price_key(market: str, asset: str) -> str:
    return f"{market.strip()}|{asset.strip()}"


def merge_asset_prices(
    stored_prices: Dict[str, int], entries, asset_prices: Optional[Dict[str, int]] = None
) -> Dict[str, int]:
    """Combine persisted prices with latest entry current_unit_price fallbacks."""
    merged: Dict[str, int] = dict(stored_prices or {})
    if asset_prices:
        merged.update(asset_prices)
    for entry in reversed(list(entries or [])):
        if getattr(entry, "is_investment_sell", False):
            continue
        if getattr(entry, "investment_direction", "buy") == "sell":
            continue
        meta = decode_investment_category(getattr(entry, "category", "") or "") or {}
        market = meta.get("market") or ""
        asset = meta.get("asset") or ""
        if not market or not asset:
            continue
        key = asset_price_key(market, asset)
        price = getattr(entry, "current_unit_price", None)
        if key not in merged and price and price > 0:
            merged[key] = int(price)
    return merged


def _entry_is_sell(entry) -> bool:
    if hasattr(entry, "is_investment_sell"):
        return bool(entry.is_investment_sell)
    return getattr(entry, "investment_direction", "buy") == "sell"


def _fmt_qty(qty: float) -> str:
    text = f"{qty:g}" if qty == int(qty) else f"{qty:.4f}".rstrip("0").rstrip(".")
    return text


def compute_positions(
    entries, asset_prices: Optional[Dict[str, int]] = None
) -> List[Dict[str, Any]]:
    """Build open holdings from buy/sell ledger (average-cost method)."""
    prices = asset_prices or {}
    buckets: Dict[str, Dict[str, Any]] = {}
    sorted_entries = sorted(
        list(entries or []),
        key=lambda e: (getattr(e, "date", ""), getattr(e, "id", 0) or 0),
    )

    for entry in sorted_entries:
        cat = getattr(entry, "category", "") or ""
        if not cat:
            continue
        meta = decode_investment_category(cat) or {}
        if cat not in buckets:
            buckets[cat] = {"meta": meta, "quantity": 0.0, "cost_basis": 0}
        bucket = buckets[cat]

        if _entry_is_sell(entry):
            qty = getattr(entry, "quantity", None)
            amount = int(getattr(entry, "amount", 0) or 0)
            if qty and qty > 0 and bucket["quantity"] > 0:
                sell_qty = min(float(qty), bucket["quantity"])
                avg = bucket["cost_basis"] / bucket["quantity"]
                bucket["quantity"] -= sell_qty
                bucket["cost_basis"] = max(0, round(bucket["cost_basis"] - avg * sell_qty))
            elif amount > 0:
                bucket["cost_basis"] = max(0, bucket["cost_basis"] - amount)
                if bucket["quantity"] > 0 and bucket["cost_basis"] == 0:
                    bucket["quantity"] = 0.0
        else:
            qty = getattr(entry, "quantity", None)
            amount = int(getattr(entry, "amount", 0) or 0)
            if qty and qty > 0:
                bucket["quantity"] += float(qty)
            if amount > 0:
                bucket["cost_basis"] += amount

    positions: List[Dict[str, Any]] = []
    for cat, bucket in buckets.items():
        cost_basis = int(bucket["cost_basis"])
        quantity = float(bucket["quantity"])
        if cost_basis <= 0 and quantity <= 0:
            continue
        if cost_basis <= 0:
            continue

        meta = bucket["meta"] or decode_investment_category(cat) or {}
        market = str(meta.get("market") or "")
        asset = str(meta.get("asset") or "")
        risk = str(meta.get("risk") or "")
        inv_meta = investment_meta_dict(meta)

        price_key = asset_price_key(market, asset)
        current_price = prices.get(price_key) if market and asset else None

        qty_out: Optional[float] = quantity if quantity > 0 else None
        avg_unit_price: Optional[int] = None
        if qty_out and cost_basis > 0:
            avg_unit_price = round(cost_basis / qty_out)
        elif not qty_out:
            avg_unit_price = cost_basis

        estimated_value = cost_basis
        has_market_price = False
        unrealized_pnl: Optional[int] = None
        unrealized_pnl_pct: Optional[float] = None

        if qty_out and current_price and current_price > 0:
            estimated_value = round(qty_out * current_price)
            has_market_price = True
            unrealized_pnl = estimated_value - cost_basis
            if cost_basis > 0:
                unrealized_pnl_pct = round(unrealized_pnl / cost_basis * 100, 2)

        positions.append({
            "category": cat,
            "key": asset or market or cat,
            "meta": inv_meta,
            "risk": risk,
            "market": market,
            "asset": asset,
            "quantity": qty_out,
            "avg_unit_price": avg_unit_price,
            "current_unit_price": current_price,
            "cost_basis": cost_basis,
            "estimated_value": estimated_value,
            "has_market_price": has_market_price,
            "unrealized_pnl": unrealized_pnl,
            "unrealized_pnl_pct": unrealized_pnl_pct,
        })

    positions.sort(key=lambda p: p["estimated_value"], reverse=True)
    return positions


def validate_investment_sell(
    category: str,
    amount: int,
    quantity: Optional[float],
    entries,
    exclude_id: Optional[int] = None,
) -> Optional[str]:
    """Return Persian error message if sell exceeds holdings."""
    if amount <= 0:
        return "مبلغ باید بزرگ‌تر از صفر باشد"
    filtered = [
        e for e in (entries or [])
        if exclude_id is None or getattr(e, "id", None) != exclude_id
    ]
    positions = compute_positions(filtered)
    pos = next((p for p in positions if p["category"] == category), None)
    available_cost = int(pos["cost_basis"]) if pos else 0
    available_qty = pos["quantity"] if pos else None

    if available_cost <= 0:
        return "موجودی این دارایی برای فروش کافی نیست"

    if quantity and quantity > 0:
        if not available_qty or available_qty <= 0:
            return "برای فروش با تعداد، ابتدا خرید با تعداد ثبت کنید"
        if quantity > available_qty + 1e-9:
            return f"حداکثر {_fmt_qty(available_qty)} واحد قابل فروش است"

    if amount > available_cost:
        return f"حداکثر {available_cost:,} تومان قابل برداشت است"

    return None


def period_buy_total(entries) -> int:
    """Sum of buy amounts in a period (for monthly deposit goals)."""
    total = 0
    for entry in entries or []:
        if _entry_is_sell(entry):
            continue
        total += int(getattr(entry, "amount", 0) or 0)
    return total


def positions_value_breakdown(positions: List[Dict[str, Any]]) -> Dict[str, Dict[str, int]]:
    by_asset: Dict[str, int] = {}
    by_risk: Dict[str, int] = {}
    for pos in positions:
        value = int(pos.get("estimated_value") or 0)
        if not value:
            continue
        asset = pos.get("asset") or pos.get("key") or "سایر"
        risk = pos.get("risk") or "سایر"
        by_asset[asset] = by_asset.get(asset, 0) + value
        by_risk[risk] = by_risk.get(risk, 0) + value
    return {"by_asset": by_asset, "by_risk": by_risk}


def is_builtin_asset(market: str, asset: str) -> bool:
    market = market.strip()
    asset = asset.strip()
    return any(a.get("value") == asset for a in INVESTMENT_ASSETS.get(market, []))


def compute_allocation_comparison(
    positions: List[Dict[str, Any]],
    targets: Dict[str, int],
) -> List[Dict[str, Any]]:
    """Compare actual portfolio weights to target allocation percentages."""
    value_breakdown = positions_value_breakdown(positions)
    by_asset = value_breakdown["by_asset"]
    total = sum(by_asset.values()) or 0

    asset_meta: Dict[str, Dict[str, str]] = {}
    for pos in positions:
        asset = str(pos.get("asset") or "")
        if asset and asset not in asset_meta:
            asset_meta[asset] = {
                "market": str(pos.get("market") or ""),
                "emoji": (pos.get("meta") or {}).get("asset_emoji") or "💎",
            }

    items: List[Dict[str, Any]] = []
    seen_assets: set = set()

    for key, target_pct in sorted((targets or {}).items(), key=lambda x: -x[1]):
        if target_pct <= 0:
            continue
        parts = str(key).split("|", 1)
        if len(parts) == 2:
            market, asset = parts[0].strip(), parts[1].strip()
        else:
            asset = parts[0].strip()
            market = asset_meta.get(asset, {}).get("market", "")
        actual_value = int(by_asset.get(asset, 0))
        actual_pct = round(actual_value / total * 100, 1) if total > 0 else 0.0
        drift = round(actual_pct - target_pct, 1)
        meta = asset_meta.get(asset, {})
        items.append({
            "key": asset_price_key(market, asset) if market and asset else asset,
            "market": market,
            "asset": asset,
            "asset_emoji": meta.get("emoji") or "💎",
            "target_pct": int(target_pct),
            "actual_pct": actual_pct,
            "actual_value": actual_value,
            "drift": drift,
        })
        seen_assets.add(asset)

    for asset, value in sorted(by_asset.items(), key=lambda x: -x[1]):
        if asset in seen_assets or not value:
            continue
        meta = asset_meta.get(asset, {})
        actual_pct = round(value / total * 100, 1) if total > 0 else 0.0
        market = meta.get("market", "")
        items.append({
            "key": asset_price_key(market, asset) if market else asset,
            "market": market,
            "asset": asset,
            "asset_emoji": meta.get("emoji") or "💎",
            "target_pct": 0,
            "actual_pct": actual_pct,
            "actual_value": int(value),
            "drift": actual_pct,
        })

    return items


def allocation_targets_total(targets: Dict[str, int]) -> int:
    return sum(int(v) for v in (targets or {}).values() if int(v) > 0)
