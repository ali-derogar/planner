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
    {"value": "اوراق بدهی", "label": "اوراق بدهی", "emoji": "📋"},
    {"value": "املاک", "label": "املاک", "emoji": "🏠"},
    {"value": "خودرو", "label": "خودرو", "emoji": "🚗"},
    {"value": "بورس کالا", "label": "بورس کالا", "emoji": "📦"},
    {"value": "رمزارز", "label": "رمزارز", "emoji": "₿"},
]

INVESTMENT_MARKET_HINTS: Dict[str, str] = {
    "فیزیکی": "طلای فیزیکی، سکه و فلزات گران‌بها (واحد: گرم یا عدد)",
    "بورس": "سهام شرکت‌های پذیرفته‌شده در بورس تهران (واحد: سهم)",
    "صندوق": "صندوق‌های ETF و درآمد ثابت (واحد: واحد صندوق)",
    "سپرده بانکی": "سپرده و گواهی سپرده بانکی (واحد: تومان)",
    "اوراق بدهی": "اوراق مشارکت و اسناد خزانه (واحد: برگه)",
    "املاک": "مسکن، زمین و ملک تجاری (واحد: متر)",
    "خودرو": "خودرو سواری، کار و موتور (واحد: دستگاه)",
    "بورس کالا": "قراردادهای کالایی بورس (واحد: قرارداد)",
    "رمزارز": "ارز دیجیتال (واحد: کوین)",
}


def _asset(
    value: str,
    label: str,
    emoji: str,
    unit: str = "واحد",
    subgroup: str = "",
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    item: Dict[str, Any] = {
        "value": value,
        "label": label,
        "emoji": emoji,
        "unit": unit,
    }
    if subgroup:
        item["subgroup"] = subgroup
    if tags:
        item["search_tags"] = tags
    return item


INVESTMENT_ASSETS: Dict[str, List[Dict[str, Any]]] = {
    "فیزیکی": [
        _asset("طلا", "طلا ۱۸ عیار", "🥇", "گرم", "فلزات", ["طلای 18", "geram18"]),
        _asset("طلا ۲۴", "طلا ۲۴ عیار", "🥇", "گرم", "فلزات", ["طلای 24"]),
        _asset("نقره", "نقره ۹۹۹", "🥈", "گرم", "فلزات", ["silver"]),
        _asset("سکه", "سکه تمام بهار", "🪙", "عدد", "سکه", ["sekee", "تمام"]),
        _asset("سکه نیم", "سکه نیم", "🪙", "عدد", "سکه", ["نیم"]),
        _asset("سکه ربع", "سکه ربع", "🪙", "عدد", "سکه", ["ربع"]),
        _asset("سکه گرمی", "سکه گرمی", "🪙", "عدد", "سکه", ["گرمی"]),
        _asset("جواهر", "جواهر", "💍", "عدد", "سایر"),
        _asset("پلاتین", "پلاتین", "⚪", "گرم", "فلزات"),
    ],
    "بورس": [
        _asset("فملی", "فملی — ملی صنایع مس", "🏭", "سهم", "فلزات", ["مس"]),
        _asset("فولاد", "فولاد — فولاد مبارکه", "🏭", "سهم", "فلزات", ["فولاد مبارکه"]),
        _asset("ذوب", "ذوب — ذوب آهن", "🔩", "سهم", "فلزات"),
        _asset("کگل", "کگل — گل‌گهر", "⛏️", "سهم", "فلزات", ["گل گهر"]),
        _asset("فارس", "فارس — پتروشیمی فارس", "⚗️", "سهم", "پتروشیمی"),
        _asset("شپنا", "شپنا — پالایش نفت اصفهان", "🛢️", "سهم", "پتروشیمی", ["پالایش"]),
        _asset("جم", "جم — جم پتروشیمی", "⚗️", "سهم", "پتروشیمی"),
        _asset("وبملت", "وبملت — بانک ملت", "🏛️", "سهم", "بانکی", ["ملت"]),
        _asset("وپاسار", "وپاسار — بانک پاسارگاد", "🏛️", "سهم", "بانکی", ["پاسارگاد"]),
        _asset("خساپا", "خساپا — ایران خودرو", "🚙", "سهم", "خودرو", ["ایران خودرو"]),
        _asset("خپارس", "خپارس — پارس خودرو", "🚗", "سهم", "خودرو"),
        _asset("رتاپ", "رتاپ — تجارت الکترونیک", "💻", "سهم", "IT"),
        _asset("آپ", "آپ — آسان پرداخت", "📱", "سهم", "IT", ["آسان پرداخت"]),
        _asset("شستا", "شستا — سرمایه‌گذاری تأمین اجتماعی", "🏢", "سهم", "هلدینگ"),
        _asset("وغدیر", "وغدیر — غدیر", "🏢", "سهم", "هلدینگ", ["غدیر"]),
        _asset("شتران", "شتران — پالایش نفت تهران", "🛢️", "سهم", "پتروشیمی"),
        _asset("شفارس", "شفارس — پتروشیمی فارس", "⚗️", "سهم", "پتروشیمی"),
        _asset("وبصادر", "وبصادر — بانک صادرات", "🏛️", "سهم", "بانکی"),
        _asset("وتجارت", "وتجارت — بانک تجارت", "🏛️", "سهم", "بانکی"),
        _asset("وبانک", "وبانک — بانک سپه", "🏛️", "سهم", "بانکی"),
        _asset("زاگرس", "زاگرس — پتروشیمی زاگرس", "⚗️", "سهم", "پتروشیمی"),
        _asset("کالا", "کالا — بورس کالا", "📦", "سهم", "سایر"),
        _asset("ومعادن", "ومعادن — توسعه معادن", "⛏️", "سهم", "فلزات"),
        _asset("فخوز", "فخوز — فولاد خوزستان", "🏭", "سهم", "فلزات"),
        _asset("سهام عمومی", "سهام — سایر نمادها", "📊", "سهم", "سایر"),
    ],
    "صندوق": [
        _asset("عیار", "عیار — ETF طلا", "✨", "واحد", "ETF", ["طلا"]),
        _asset("نقرابی", "نقرابی — ETF نقره", "🥈", "واحد", "ETF", ["نقره"]),
        _asset("کهربا", "کهربا — ETF درآمد ثابت", "🟠", "واحد", "ETF"),
        _asset("آگاس", "آگاس — ETF نقره", "🔷", "واحد", "ETF"),
        _asset("دارا", "دارا — ETF سهام", "📈", "واحد", "ETF"),
        _asset("پالایش", "پالایش — ETF پالایشی", "🛢️", "واحد", "ETF"),
        _asset("سهام", "سهام — ETF بورسی", "📊", "واحد", "ETF"),
        _asset("درآمد ثابت", "درآمد ثابت", "💵", "واحد", "درآمد ثابت"),
        _asset("صندوق با درآمد ثابت", "صندوق با درآمد ثابت", "💰", "واحد", "درآمد ثابت"),
        _asset("صندوق مختلط", "صندوق مختلط", "🔀", "واحد", "درآمد ثابت"),
    ],
    "سپرده بانکی": [
        _asset("کوتاه‌مدت", "سپرده کوتاه‌مدت", "📅", "تومان"),
        _asset("بلندمدت", "سپرده بلندمدت", "🗓️", "تومان"),
        _asset("گواهی سپرده", "گواهی سپرده", "📜", "برگه"),
        _asset("سپرده ارزی", "سپرده ارزی", "💱", "واحد ارز"),
    ],
    "اوراق بدهی": [
        _asset("اوراق مشارکت", "اوراق مشارکت", "📋", "برگه"),
        _asset("اسناد خزانه", "اسناد خزانه (اخزا)", "🏛️", "برگه", tags=["اخزا"]),
        _asset("اوراق مرابحه", "اوراق مرابحه", "📄", "برگه"),
        _asset("اوراق صکوک", "اوراق صکوک", "🕌", "برگه"),
    ],
    "املاک": [
        _asset("مسکن", "مسکن", "🏠", "متر"),
        _asset("زمین", "زمین", "🌍", "متر"),
        _asset("تجاری", "ملک تجاری", "🏢", "متر"),
        _asset("پیش‌فروش", "پیش‌فروش مسکن", "🏗️", "متر"),
    ],
    "خودرو": [
        _asset("سواری", "خودرو سواری", "🚗", "دستگاه"),
        _asset("کار", "خودرو کار", "🚚", "دستگاه"),
        _asset("موتور", "موتورسیکلت", "🏍️", "دستگاه"),
        _asset("پراید", "پراید", "🚗", "دستگاه", "برند"),
        _asset("پژو ۲۰۶", "پژو ۲۰۶", "🚗", "دستگاه", "برند"),
        _asset("سمند", "سمند", "🚗", "دستگاه", "برند"),
    ],
    "بورس کالا": [
        _asset("زرین", "زرین — زعفران", "🌾", "قرارداد", tags=["زعفران"]),
        _asset("پنبه", "پنبه", "☁️", "قرارداد"),
        _asset("سیمان", "سیمان", "🧱", "قرارداد"),
        _asset("فولاد کالا", "فولاد کالا", "🔩", "قرارداد"),
        _asset("نفت", "نفت خام", "🛢️", "قرارداد"),
    ],
    "رمزارز": [
        _asset("BTC/USDT", "BTC/USDT — بیت‌کوین", "₿", "BTC", tags=["bitcoin"]),
        _asset("ETH/USDT", "ETH/USDT — اتریوم", "⟠", "ETH", tags=["ethereum"]),
        _asset("BNB/USDT", "BNB/USDT", "🔶", "BNB"),
        _asset("XRP/USDT", "XRP/USDT — ریپل", "💧", "XRP", tags=["ripple"]),
        _asset("SOL/USDT", "SOL/USDT — سولانا", "◎", "SOL"),
        _asset("TON/USDT", "TON/USDT", "💎", "TON"),
        _asset("TRX/USDT", "TRX/USDT — ترون", "🔺", "TRX", tags=["tron"]),
        _asset("DOGE/USDT", "DOGE/USDT — دوج‌کوین", "🐕", "DOGE"),
        _asset("ADA/USDT", "ADA/USDT — کاردانو", "🔵", "ADA"),
        _asset("SHIB/USDT", "SHIB/USDT — شیبا", "🐾", "SHIB"),
        _asset("USDT/IRT", "USDT — تتر", "💲", "USDT", tags=["tether", "تتر"]),
        _asset("LTC/USDT", "LTC/USDT — لایت‌کوین", "Ł", "LTC"),
        _asset("DOT/USDT", "DOT/USDT — پولkadot", "🔴", "DOT"),
        _asset("AVAX/USDT", "AVAX/USDT — آوالanche", "🔺", "AVAX"),
    ],
}

INVESTMENT_RISK_MARKETS: Dict[str, List[str]] = {
    "بدون ریسک": ["سپرده بانکی", "صندوق", "اوراق بدهی"],
    "کم ریسک": ["فیزیکی", "صندوق", "اوراق بدهی"],
    "ریسک متوسط": ["بورس", "املاک", "خودرو", "بورس کالا", "صندوق"],
    "پر ریسک": ["بورس", "رمزارز"],
}

_MARKET_DEFAULT_RISK: Dict[str, str] = {
    "سپرده بانکی": "بدون ریسک",
    "اوراق بدهی": "بدون ریسک",
    "فیزیکی": "کم ریسک",
    "صندوق": "کم ریسک",
    "بورس": "ریسک متوسط",
    "املاک": "ریسک متوسط",
    "خودرو": "ریسک متوسط",
    "بورس کالا": "ریسک متوسط",
    "رمزارز": "پر ریسک",
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


def normalize_investment_meta(
    meta: Optional[Dict[str, str]],
    assets_map: Optional[Dict[str, List[Dict[str, Any]]]] = None,
) -> Dict[str, str]:
    """Fill missing risk/market for legacy or partial categories."""
    if not meta:
        return {"risk": "", "market": "", "asset": ""}
    risk = (meta.get("risk") or "").strip()
    market = (meta.get("market") or "").strip()
    asset = (meta.get("asset") or "").strip()
    if risk and market and asset:
        return {"risk": risk, "market": market, "asset": asset}
    if not market and not risk and asset in _LEGACY_CATEGORY_MAP:
        r, m, a = _LEGACY_CATEGORY_MAP[asset]
        return {"risk": r, "market": m, "asset": a}
    catalog = assets_map or INVESTMENT_ASSETS
    if market and asset:
        if not risk:
            risk = _MARKET_DEFAULT_RISK.get(market, "")
            if not risk:
                for r, mkts in INVESTMENT_RISK_MARKETS.items():
                    if market in mkts:
                        risk = r
                        break
        return {"risk": risk, "market": market, "asset": asset}
    if asset and not market:
        markets = [
            mkt for mkt, items in catalog.items()
            if any(i.get("value") == asset for i in items)
        ]
        if len(markets) == 1:
            mkt = markets[0]
            for r, mkts in INVESTMENT_RISK_MARKETS.items():
                if mkt in mkts:
                    return {"risk": r, "market": mkt, "asset": asset}
    return {"risk": risk, "market": market, "asset": asset}


def canonical_investment_category(
    category: str,
    assets_map: Optional[Dict[str, List[Dict[str, Any]]]] = None,
) -> str:
    """Stable encoded key for the same logical asset across legacy and JSON rows."""
    if not category:
        return ""
    text = category.strip()
    if text in _LEGACY_CATEGORY_MAP:
        r, m, a = _LEGACY_CATEGORY_MAP[text]
        return encode_investment_category(r, m, a)
    meta = normalize_investment_meta(decode_investment_category(text), assets_map)
    if meta.get("risk") and meta.get("market") and meta.get("asset"):
        return encode_investment_category(meta["risk"], meta["market"], meta["asset"])
    return text


def asset_price_key(market: str, asset: str) -> str:
    return f"{market.strip()}|{asset.strip()}"


def markets_for_risk(risk: str) -> List[Dict[str, str]]:
    keys = INVESTMENT_RISK_MARKETS.get(risk.strip(), [])
    return [m for m in INVESTMENT_MARKETS if m["value"] in keys]


def is_valid_risk_market(risk: str, market: str) -> bool:
    return market.strip() in INVESTMENT_RISK_MARKETS.get(risk.strip(), [])


def find_asset(
    market: str,
    asset: str,
    assets_map: Optional[Dict[str, List[Dict[str, Any]]]] = None,
) -> Optional[Dict[str, Any]]:
    market = market.strip()
    asset = asset.strip()
    catalog = assets_map if assets_map is not None else INVESTMENT_ASSETS
    for item in catalog.get(market, []):
        if item.get("value") == asset or item.get("label") == asset:
            return item
    return None


def asset_unit(
    market: str,
    asset: str,
    assets_map: Optional[Dict[str, List[Dict[str, Any]]]] = None,
) -> str:
    found = find_asset(market, asset, assets_map)
    return str(found.get("unit") or "واحد") if found else "واحد"


def assets_for_market(
    market: str,
    assets_map: Optional[Dict[str, List[Dict[str, Any]]]] = None,
) -> List[Dict[str, Any]]:
    return list((assets_map or INVESTMENT_ASSETS).get(market.strip(), []))


def _count_builtin_assets() -> int:
    return sum(len(v) for v in INVESTMENT_ASSETS.values())


def _build_units_map(
    assets_map: Dict[str, List[Dict[str, Any]]],
) -> Dict[str, str]:
    units: Dict[str, str] = {}
    for market, items in assets_map.items():
        for item in items:
            value = str(item.get("value") or "")
            if value:
                units[asset_price_key(market, value)] = str(item.get("unit") or "واحد")
    return units


def get_investment_taxonomy() -> dict:
    return {
        "risks": INVESTMENT_RISKS,
        "markets": INVESTMENT_MARKETS,
        "market_hints": INVESTMENT_MARKET_HINTS,
        "markets_by_risk": {
            risk["value"]: markets_for_risk(risk["value"]) for risk in INVESTMENT_RISKS
        },
        "assets": INVESTMENT_ASSETS,
        "units": _build_units_map(INVESTMENT_ASSETS),
        "asset_count": _count_builtin_assets(),
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


def investment_meta_dict(
    meta: Optional[Dict[str, str]],
    assets_map: Optional[Dict[str, List[Dict[str, Any]]]] = None,
) -> Dict[str, Any]:
    if not meta:
        return {}
    risk = meta.get("risk") or ""
    market = meta.get("market") or ""
    asset = meta.get("asset") or ""
    catalog = assets_map or INVESTMENT_ASSETS
    risk_emoji = _emoji_for(INVESTMENT_RISKS, risk, "📊")
    market_emoji = _emoji_for(INVESTMENT_MARKETS, market, "💼")
    asset_item = find_asset(market, asset, catalog)
    asset_emoji = (asset_item or {}).get("emoji") or _emoji_for(
        catalog.get(market, []), asset, "💎"
    )
    unit = str((asset_item or {}).get("unit") or "واحد")
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
        "unit": unit,
        "risk_emoji": risk_emoji,
        "market_emoji": market_emoji,
        "asset_emoji": asset_emoji,
        "display": " · ".join(parts),
        "group_key": asset or market or risk,
    }


def investment_group_key(category: str) -> str:
    meta = normalize_investment_meta(decode_investment_category(category))
    if not meta.get("asset") and not meta.get("market"):
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
        entry: Dict[str, Any] = {
            "value": value,
            "label": str(item.get("label") or value),
            "emoji": str(item.get("emoji") or "💎"),
            "unit": str(item.get("unit") or "واحد"),
        }
        tags = item.get("search_tags")
        if tags:
            entry["search_tags"] = tags if isinstance(tags, list) else [str(tags)]
        assets[market].append(entry)
    return {
        **taxonomy,
        "assets": assets,
        "units": _build_units_map(assets),
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
        key = normalize_investment_meta(
            decode_investment_category(entry.category or "") or {}
        ).get("asset") or investment_group_key(entry.category or "")
        by_asset[key] = by_asset.get(key, 0) + signed
        meta = normalize_investment_meta(decode_investment_category(entry.category or "") or {})
        risk = meta.get("risk") or "سایر"
        by_risk[risk] = by_risk.get(risk, 0) + signed
    return {"by_asset": by_asset, "by_risk": by_risk}


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
    entries,
    asset_prices: Optional[Dict[str, int]] = None,
    assets_map: Optional[Dict[str, List[Dict[str, Any]]]] = None,
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
        bucket_key = canonical_investment_category(cat)
        meta = normalize_investment_meta(decode_investment_category(cat))
        if bucket_key not in buckets:
            buckets[bucket_key] = {"meta": meta, "quantity": 0.0, "cost_basis": 0}
        bucket = buckets[bucket_key]

        if _entry_is_sell(entry):
            qty = getattr(entry, "quantity", None)
            amount = int(getattr(entry, "amount", 0) or 0)
            if qty and qty > 0 and bucket["quantity"] > 0:
                sell_qty = min(float(qty), bucket["quantity"])
                avg = bucket["cost_basis"] / bucket["quantity"]
                bucket["quantity"] -= sell_qty
                bucket["cost_basis"] = max(0, round(bucket["cost_basis"] - avg * sell_qty))
            elif amount > 0:
                if bucket["quantity"] > 0 and bucket["cost_basis"] > 0:
                    avg = bucket["cost_basis"] / bucket["quantity"]
                    sell_qty = min(bucket["quantity"], amount / avg)
                    bucket["quantity"] = max(0.0, bucket["quantity"] - sell_qty)
                    bucket["cost_basis"] = max(0, round(bucket["cost_basis"] - avg * sell_qty))
                else:
                    bucket["cost_basis"] = max(0, bucket["cost_basis"] - amount)
        else:
            qty = getattr(entry, "quantity", None)
            amount = int(getattr(entry, "amount", 0) or 0)
            unit = getattr(entry, "unit_price", None)
            if qty and qty > 0:
                bucket["quantity"] += float(qty)
            elif amount > 0 and unit and unit > 0:
                bucket["quantity"] += amount / unit
            if amount > 0:
                bucket["cost_basis"] += amount

    positions: List[Dict[str, Any]] = []
    for bucket_key, bucket in buckets.items():
        cost_basis = int(bucket["cost_basis"])
        quantity = float(bucket["quantity"])
        if cost_basis <= 0 and quantity <= 0:
            continue
        if cost_basis <= 0:
            continue

        meta = bucket["meta"] or normalize_investment_meta(decode_investment_category(bucket_key))
        market = str(meta.get("market") or "")
        asset = str(meta.get("asset") or "")
        risk = str(meta.get("risk") or "")
        inv_meta = investment_meta_dict(meta, assets_map)

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
            "category": bucket_key,
            "key": asset or market or bucket_key,
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


def _credit_excluded_entry_to_availability(
    excluded_entry,
    target: str,
    available_cost: int,
    available_qty: Optional[float],
) -> tuple:
    if not excluded_entry:
        return available_cost, available_qty
    if canonical_investment_category(getattr(excluded_entry, "category", "") or "") != target:
        return available_cost, available_qty
    amount = int(getattr(excluded_entry, "amount", 0) or 0)
    if not _entry_is_sell(excluded_entry):
        return available_cost, available_qty
    available_cost += amount
    exc_qty = getattr(excluded_entry, "quantity", None)
    if exc_qty and exc_qty > 0:
        available_qty = (available_qty or 0) + float(exc_qty)
    return available_cost, available_qty


def _sells_total_for_category(entries, target: str) -> tuple:
    sold_cost = 0
    sold_qty = 0.0
    tracks_qty = False
    for entry in entries or []:
        if not _entry_is_sell(entry):
            continue
        if canonical_investment_category(getattr(entry, "category", "") or "") != target:
            continue
        sold_cost += int(getattr(entry, "amount", 0) or 0)
        qty = getattr(entry, "quantity", None)
        if qty and qty > 0:
            sold_qty += float(qty)
            tracks_qty = True
    return sold_cost, sold_qty if tracks_qty else None


def validate_investment_buy_edit(
    category: str,
    amount: int,
    quantity: Optional[float],
    entries,
    exclude_id: Optional[int] = None,
    old_category: Optional[str] = None,
    unit_price: Optional[int] = None,
    entry_date=None,
) -> Optional[str]:
    """Ensure editing a buy doesn't break existing sells."""
    if exclude_id is None:
        return None
    target = canonical_investment_category(category)
    old_target = canonical_investment_category(old_category or category)
    filtered = [
        e for e in (entries or [])
        if getattr(e, "id", None) != exclude_id
    ]
    if old_target != target:
        for entry in filtered:
            if (
                _entry_is_sell(entry)
                and canonical_investment_category(getattr(entry, "category", "") or "")
                == old_target
            ):
                return "دارایی را نمی‌توان تغییر داد وقتی فروش ثبت شده است"
    sold_cost, sold_qty = _sells_total_for_category(filtered, target)
    if sold_cost > 0 and amount < sold_cost:
        return f"مبلغ خرید باید حداقل {sold_cost:,} تومان باشد (جمع فروش‌ها)"
    if sold_qty and sold_qty > 0:
        effective_qty = quantity
        if (not effective_qty or effective_qty <= 0) and amount > 0 and unit_price and unit_price > 0:
            effective_qty = amount / unit_price
        if not effective_qty or effective_qty <= 0:
            return f"تعداد الزامی است (حداقل {_fmt_qty(sold_qty)} واحد)"
        if effective_qty + 1e-9 < sold_qty:
            return f"تعداد باید حداقل {_fmt_qty(sold_qty)} باشد"
    if entry_date is not None:
        from dailyplanner.models import str_to_date

        for entry in filtered:
            if not _entry_is_sell(entry):
                continue
            if canonical_investment_category(getattr(entry, "category", "") or "") != target:
                continue
            try:
                sell_date = str_to_date(entry.date)
            except (ValueError, TypeError):
                continue
            if entry_date > sell_date:
                return "تاریخ خرید نمی‌تواند بعد از فروش‌های این دارایی باشد"
        replay_err = _validate_buy_edit_ledger(
            category, amount, quantity, unit_price, filtered, target, entry_date
        )
        if replay_err:
            return replay_err
    return None


def _validate_buy_edit_ledger(
    category: str,
    amount: int,
    quantity: Optional[float],
    unit_price: Optional[int],
    entries,
    target: str,
    entry_date,
) -> Optional[str]:
    """Replay ledger with the proposed buy and ensure each sell still fits."""
    from dailyplanner.models import str_to_date

    class _ProposedBuy:
        id = -1

        def __init__(self):
            self.date = entry_date.isoformat() if hasattr(entry_date, "isoformat") else str(entry_date)
            self.category = category
            self.amount = amount
            self.investment_direction = "buy"
            self.quantity = quantity
            self.unit_price = unit_price

    rows = sorted(
        list(entries or []) + [_ProposedBuy()],
        key=lambda e: (getattr(e, "date", ""), getattr(e, "id", 0) or 0),
    )

    def _entry_date(entry) -> str:
        return getattr(entry, "date", "") or ""

    for row in rows:
        if not _entry_is_sell(row):
            continue
        if canonical_investment_category(getattr(row, "category", "") or "") != target:
            continue
        try:
            as_of = str_to_date(_entry_date(row))
        except (ValueError, TypeError):
            continue
        subset = [
            e for e in rows
            if _entry_date(e) and str_to_date(_entry_date(e)) <= as_of
        ]
        sell_err = validate_investment_sell(
            row.category,
            int(getattr(row, "amount", 0) or 0),
            getattr(row, "quantity", None),
            subset,
        )
        if sell_err:
            return "ویرایش باعث می‌شود فروش‌های ثبت‌شده از موجودی بیشتر باشند"
    return None


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
    excluded_entry = None
    if exclude_id is not None:
        for entry in entries or []:
            if getattr(entry, "id", None) == exclude_id:
                excluded_entry = entry
                break
    filtered = [
        e for e in (entries or [])
        if exclude_id is None or getattr(e, "id", None) != exclude_id
    ]
    positions = compute_positions(filtered)
    target = canonical_investment_category(category)
    pos = next((p for p in positions if p["category"] == target), None)
    available_cost = int(pos["cost_basis"]) if pos else 0
    available_qty = pos["quantity"] if pos else None
    available_cost, available_qty = _credit_excluded_entry_to_availability(
        excluded_entry, target, available_cost, available_qty
    )

    if available_cost <= 0:
        return "موجودی این دارایی برای فروش کافی نیست"

    if quantity and quantity > 0:
        if not available_qty or available_qty <= 0:
            return "برای فروش با تعداد، ابتدا خرید با تعداد ثبت کنید"
        if quantity > available_qty + 1e-9:
            return f"حداکثر {_fmt_qty(available_qty)} واحد قابل فروش است"
        avg_cost = available_cost / available_qty
        expected_amount = max(1, round(quantity * avg_cost))
        if amount > expected_amount:
            return f"حداکثر {expected_amount:,} تومان برای {_fmt_qty(quantity)} واحد"
        if abs(amount - expected_amount) > max(100, round(expected_amount * 0.005)):
            return f"مبلغ باید {expected_amount:,} تومان باشد (بر اساس میانگین بهای تمام‌شده)"

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


def _positions_value_by_market_asset(positions: List[Dict[str, Any]]) -> Dict[str, int]:
    by_key: Dict[str, int] = {}
    for pos in positions:
        value = int(pos.get("estimated_value") or 0)
        if not value:
            continue
        market = str(pos.get("market") or "")
        asset = str(pos.get("asset") or "")
        key = asset_price_key(market, asset) if market and asset else str(pos.get("key") or "سایر")
        by_key[key] = by_key.get(key, 0) + value
    return by_key


def positions_value_breakdown(positions: List[Dict[str, Any]]) -> Dict[str, Dict[str, int]]:
    by_asset: Dict[str, int] = {}
    by_risk: Dict[str, int] = {}
    for pos in positions:
        value = int(pos.get("estimated_value") or 0)
        if not value:
            continue
        asset = pos.get("asset") or pos.get("key") or "سایر"
        market = str(pos.get("market") or "")
        asset_key = asset_price_key(market, asset) if market and asset else str(asset)
        risk = pos.get("risk") or "سایر"
        by_asset[asset_key] = by_asset.get(asset_key, 0) + value
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
    by_key = _positions_value_by_market_asset(positions)
    total = sum(by_key.values()) or 0

    asset_meta: Dict[str, Dict[str, str]] = {}
    for pos in positions:
        market = str(pos.get("market") or "")
        asset = str(pos.get("asset") or "")
        pos_key = asset_price_key(market, asset) if market and asset else str(pos.get("key") or "")
        if pos_key and pos_key not in asset_meta:
            asset_meta[pos_key] = {
                "market": market,
                "asset": asset,
                "emoji": (pos.get("meta") or {}).get("asset_emoji") or "💎",
            }

    items: List[Dict[str, Any]] = []
    seen_keys: set = set()

    for key, target_pct in sorted((targets or {}).items(), key=lambda x: -x[1]):
        if target_pct <= 0:
            continue
        parts = str(key).split("|", 1)
        if len(parts) == 2:
            market, asset = parts[0].strip(), parts[1].strip()
        else:
            asset = parts[0].strip()
            market = ""
        lookup_key = asset_price_key(market, asset) if market and asset else asset
        actual_value = int(by_key.get(lookup_key, 0))
        actual_pct = round(actual_value / total * 100, 1) if total > 0 else 0.0
        drift = round(actual_pct - target_pct, 1)
        meta = asset_meta.get(lookup_key, {})
        items.append({
            "key": lookup_key,
            "market": market or meta.get("market", ""),
            "asset": asset or meta.get("asset", ""),
            "asset_emoji": meta.get("emoji") or "💎",
            "target_pct": int(target_pct),
            "actual_pct": actual_pct,
            "actual_value": actual_value,
            "drift": drift,
        })
        seen_keys.add(lookup_key)

    for pos_key, value in sorted(by_key.items(), key=lambda x: -x[1]):
        if pos_key in seen_keys or not value:
            continue
        meta = asset_meta.get(pos_key, {})
        actual_pct = round(value / total * 100, 1) if total > 0 else 0.0
        market = meta.get("market", "")
        asset = meta.get("asset", "")
        if not asset and "|" in pos_key:
            market, asset = pos_key.split("|", 1)
        items.append({
            "key": pos_key,
            "market": market,
            "asset": asset or pos_key,
            "asset_emoji": meta.get("emoji") or "💎",
            "target_pct": 0,
            "actual_pct": actual_pct,
            "actual_value": int(value),
            "drift": actual_pct,
        })

    return items


def allocation_targets_total(targets: Dict[str, int]) -> int:
    return sum(int(v) for v in (targets or {}).values() if int(v) > 0)


def _portfolio_total_value(positions: List[Dict[str, Any]]) -> int:
    return sum(int(p.get("estimated_value") or 0) for p in (positions or []))


def compute_rebalance_suggestions(
    positions: List[Dict[str, Any]],
    targets: Dict[str, int],
    available_cash: int = 0,
    drift_threshold: float = 1.0,
) -> Dict[str, Any]:
    """Suggest buy/sell amounts per asset to match target allocation."""
    total = _portfolio_total_value(positions)
    targets_total = allocation_targets_total(targets)
    empty: Dict[str, Any] = {
        "items": [],
        "portfolio_value": total,
        "total_buy": 0,
        "total_sell": 0,
        "net_cash_needed": 0,
        "available_cash": max(0, int(available_cash or 0)),
        "can_rebalance": False,
        "has_suggestions": False,
        "targets_valid": targets_total <= 100,
    }
    if total <= 0 or not targets or targets_total <= 0 or targets_total > 100:
        return empty

    comparison = compute_allocation_comparison(positions, targets)
    pos_lookup: Dict[str, Dict[str, Any]] = {}
    for pos in positions:
        pos_lookup[pos["category"]] = pos
        market = str(pos.get("market") or "")
        asset = str(pos.get("asset") or "")
        if market and asset:
            pos_lookup[asset_price_key(market, asset)] = pos
    items: List[Dict[str, Any]] = []
    total_buy = 0
    total_sell = 0
    sell_capped = False

    for row in comparison:
        target_pct = int(row.get("target_pct") or 0)
        if target_pct <= 0:
            continue
        actual_value = int(row.get("actual_value") or 0)
        target_value = round(total * target_pct / 100)
        delta = target_value - actual_value
        drift = float(row.get("drift") or 0)

        if abs(drift) <= drift_threshold and abs(delta) < max(10000, total // 200):
            action = "hold"
            amount = 0
        elif delta > 0:
            action = "buy"
            amount = delta
            total_buy += amount
        elif delta < 0:
            action = "sell"
            amount = -delta
            lookup_key = str(row.get("key") or "")
            if not lookup_key:
                market = str(row.get("market") or "")
                asset = str(row.get("asset") or "")
                lookup_key = asset_price_key(market, asset) if market and asset else asset
            pos = pos_lookup.get(lookup_key)
            if pos:
                cap = int(pos.get("cost_basis") or 0)
                if amount > cap:
                    sell_capped = True
                amount = min(amount, cap)
            total_sell += amount
        else:
            action = "hold"
            amount = 0

        items.append({
            **row,
            "target_value": target_value,
            "action": action,
            "amount": amount,
        })

    items.sort(
        key=lambda x: (
            0 if x["action"] == "buy" else 1 if x["action"] == "sell" else 2,
            -x["amount"],
        )
    )

    cash = max(0, int(available_cash or 0))
    net_cash_needed = max(0, total_buy - total_sell - cash)
    has_suggestions = any(i["action"] in ("buy", "sell") for i in items)

    return {
        "items": items,
        "portfolio_value": total,
        "total_buy": total_buy,
        "total_sell": total_sell,
        "net_cash_needed": net_cash_needed,
        "available_cash": cash,
        "can_rebalance": has_suggestions and net_cash_needed == 0 and not sell_capped,
        "has_suggestions": has_suggestions,
        "targets_valid": True,
        "sell_capped": sell_capped,
    }
