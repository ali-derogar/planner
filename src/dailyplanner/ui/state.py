"""Build JSON state for the SPA WebView client."""
import calendar
import datetime
from typing import Any, Dict, List, Optional, Set

import jdatetime

from dailyplanner.database import Database
from dailyplanner.models import (
    DailyTask,
    DailyWellness,
    FinanceEntry,
    ImportantDate,
    Installment,
    Project,
    ProjectTask,
    format_clock_time,
    format_duration,
    format_money,
    format_sleep_duration,
    str_to_date,
)
from dailyplanner.services.timer import TimerService
from dailyplanner.investments import (
    compute_allocation_comparison,
    allocation_targets_total,
    compute_positions,
    decode_investment_category,
    get_investment_taxonomy,
    investment_group_key,
    investment_meta_dict,
    investment_pnl_percent,
    merge_asset_prices,
    merge_custom_assets,
    period_buy_total,
    portfolio_breakdown,
    positions_value_breakdown,
)
from dailyplanner.ui.tokens import (
    BUDGET_EXCLUDED_CATEGORIES,
    FINANCE_CATEGORIES,
    IMPORTANT_DATE_CATEGORIES,
    MOOD_EMOJIS,
    PROJECT_COLORS,
)
from dailyplanner.utils.jalali import (
    current_jalali_ym,
    format_jalali,
    gregorian_to_jalali_parts,
    jalali_month_bounds,
    jalali_to_gregorian,
    to_persian_digits,
)

DASH = "\u2014"


def _task_dict(
    task: DailyTask,
    expanded: Set[int],
    active_id: Optional[int],
    timer_elapsed: int,
) -> dict:
    is_running = task.id == active_id
    display_sec = task.duration_seconds + (timer_elapsed if is_running else 0)
    remaining = task.remaining_seconds(display_sec)
    progress = 0
    if task.estimated_seconds > 0:
        progress = min(100, int(display_sec / task.estimated_seconds * 100))
    return {
        "id": task.id,
        "title": task.title,
        "duration": task.duration_seconds,
        "display_sec": display_sec,
        "display_fmt": format_duration(display_sec),
        "estimated": task.estimated_seconds,
        "estimated_fmt": format_duration(task.estimated_seconds) if task.estimated_seconds else DASH,
        "remaining": remaining,
        "remaining_fmt": format_duration(remaining) if remaining is not None else None,
        "progress": progress,
        "is_useful": task.is_useful,
        "is_starred": task.is_starred,
        "is_running": is_running,
        "is_expanded": task.id in expanded,
    }


def _safe_jalali_label(date_str: str) -> str:
    try:
        return format_jalali(str_to_date(date_str))
    except ValueError:
        return date_str


def _investment_taxonomy_for_db(db: Database) -> dict:
    return merge_custom_assets(get_investment_taxonomy(), db.get_investment_custom_assets())


def _investment_categories_for_db(db: Database) -> List[str]:
    tax = _investment_taxonomy_for_db(db)
    labels: List[str] = []
    for items in tax.get("assets", {}).values():
        for item in items:
            labels.append(item["label"])
    return labels


def _category_breakdown_list(by_map: Dict[str, int], total: int) -> List[dict]:
    items = []
    denom = abs(total) if total else sum(abs(v) for v in by_map.values())
    for cat, cat_amount in sorted(by_map.items(), key=lambda x: abs(x[1]), reverse=True):
        if not cat_amount:
            continue
        items.append({
            "category": cat,
            "amount": cat_amount,
            "amount_fmt": format_money(abs(cat_amount)),
            "pct": int(abs(cat_amount) / denom * 100) if denom > 0 else 0,
        })
    return items


def _position_dict(pos: dict) -> dict:
    meta = pos.get("meta") or {}
    qty = pos.get("quantity")
    avg = pos.get("avg_unit_price")
    current = pos.get("current_unit_price")
    cost = int(pos.get("cost_basis") or 0)
    est = int(pos.get("estimated_value") or cost)
    pnl = pos.get("unrealized_pnl")
    pnl_pct = pos.get("unrealized_pnl_pct")
    d = {
        "category": pos.get("category") or "",
        "key": pos.get("key") or "",
        "asset": pos.get("asset") or "",
        "market": pos.get("market") or "",
        "risk": pos.get("risk") or "",
        "display": meta.get("display") or pos.get("asset") or "",
        "asset_emoji": meta.get("asset_emoji") or "💎",
        "cost_basis": cost,
        "cost_basis_fmt": format_money(cost),
        "estimated_value": est,
        "estimated_value_fmt": format_money(est),
        "has_market_price": bool(pos.get("has_market_price")),
    }
    if qty is not None:
        d["quantity"] = qty
        d["quantity_fmt"] = _format_quantity(qty)
    if avg:
        d["avg_unit_price"] = avg
        d["avg_unit_price_fmt"] = format_money(avg)
    if current:
        d["current_unit_price"] = current
        d["current_unit_price_fmt"] = format_money(current)
    if qty and avg:
        d["qty_display"] = f"{_format_quantity(qty)} × {format_money(avg)}"
    if pnl is not None:
        sign = "+" if pnl > 0 else ""
        d["unrealized_pnl"] = pnl
        d["unrealized_pnl_fmt"] = f"{sign}{format_money(abs(pnl))}"
        d["pnl_positive"] = pnl >= 0
    if pnl_pct is not None:
        sign = "+" if pnl_pct > 0 else ""
        d["unrealized_pnl_pct"] = pnl_pct
        d["unrealized_pnl_pct_fmt"] = f"{sign}{to_persian_digits(f'{pnl_pct:g}')}٪"
    return d


def _format_quantity(qty: float) -> str:
    text = f"{qty:g}" if qty == int(qty) else f"{qty:.4f}".rstrip("0").rstrip(".")
    return to_persian_digits(text)


def _finance_dict(entry: FinanceEntry) -> dict:
    d = {
        "id": entry.id,
        "title": entry.title,
        "amount": entry.amount,
        "amount_fmt": format_money(entry.amount),
        "type": entry.entry_type,
        "category": entry.category or "عمومی",
    }
    if entry.is_investment:
        meta = decode_investment_category(entry.category or "")
        inv = investment_meta_dict(meta)
        d["investment_meta"] = inv
        d["investment_direction"] = entry.investment_direction or "buy"
        d["is_sell"] = entry.is_investment_sell
        if entry.quantity is not None:
            d["quantity"] = entry.quantity
            d["quantity_fmt"] = _format_quantity(entry.quantity)
        if entry.unit_price is not None:
            d["unit_price"] = entry.unit_price
            d["unit_price_fmt"] = format_money(entry.unit_price)
        if entry.current_unit_price is not None:
            d["current_unit_price"] = entry.current_unit_price
            d["current_unit_price_fmt"] = format_money(entry.current_unit_price)
        pnl = investment_pnl_percent(entry.unit_price, entry.current_unit_price)
        if pnl is not None:
            sign = "+" if pnl > 0 else ""
            d["pnl_percent"] = pnl
            d["pnl_fmt"] = f"{sign}{to_persian_digits(f'{pnl:g}')}٪"
            d["pnl_positive"] = pnl >= 0
        if entry.quantity is not None and entry.unit_price is not None:
            d["qty_display"] = f"{_format_quantity(entry.quantity)} × {format_money(entry.unit_price)}"
        if inv.get("display"):
            d["category_display"] = inv["display"]
        if inv.get("group_key"):
            d["category"] = inv["group_key"]
    return d


def _finance_dict_with_date(entry: FinanceEntry) -> dict:
    d = _finance_dict(entry)
    d["date"] = entry.date
    d["date_label"] = _safe_jalali_label(entry.date)
    return d


def _wellness_dict(w: Optional[DailyWellness]) -> dict:
    if w is None:
        return {
            "sleep": DASH,
            "wake": DASH,
            "sleep_dur": DASH,
            "mood": None,
            "sleep_raw": "",
            "wake_raw": "",
        }
    return {
        "sleep": format_clock_time(w.sleep_minutes),
        "wake": format_clock_time(w.wake_minutes),
        "sleep_dur": format_sleep_duration(w.sleep_duration_minutes()),
        "mood": w.mood_score,
        "sleep_raw": _fmt_hm(w.sleep_minutes),
        "wake_raw": _fmt_hm(w.wake_minutes),
    }


def _fmt_hm(minutes: Optional[int]) -> str:
    if minutes is None:
        return ""
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def all_finance_categories(db: Database) -> List[str]:
    merged = list(FINANCE_CATEGORIES)
    for cat in db.get_finance_custom_categories():
        if cat not in merged:
            merged.append(cat)
    return merged


def build_calendar_month(year: int, month: int, db: Database) -> dict:
    jd = jdatetime.date(year, month, 1)
    days_in_month = jdatetime.j_days_in_month[month - 1]
    if month == 12 and jd.isleap():
        days_in_month = 30
    cells = []
    for day in range(1, days_in_month + 1):
        g = jalali_to_gregorian(year, month, day)
        useful, not_useful = db.get_useful_totals(g)
        classified = useful + not_useful
        eff = int(useful / classified * 100) if classified > 0 else 0
        cells.append({
            "day": day,
            "date": g.isoformat(),
            "eff": eff,
            "has_data": db.get_day_activity_seconds(g) > 0,
        })
    return {
        "year": year,
        "month": month,
        "month_name": _jalali_month_name(month),
        "cells": cells,
        "weekday_offset": jd.weekday(),
    }


def _jalali_month_name(month: int) -> str:
    names = [
        "", "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
        "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند",
    ]
    return names[month]


def _compact_jalali(d: datetime.date) -> str:
    jy, jm, jd = gregorian_to_jalali_parts(d)
    return to_persian_digits(f"{jy}/{jm:02d}/{jd:02d}")


def _resolve_invest_filter_bounds(
    mode: str,
    filter_year: Optional[int],
    filter_month: Optional[int],
    filter_start: Optional[datetime.date],
    filter_end: Optional[datetime.date],
    today: datetime.date,
) -> tuple:
    """Return (period_start, period_end, label, is_current_month, goal_jy, goal_jm, bounded)."""
    cur_jy, cur_jm = current_jalali_ym(today)

    if mode == "month":
        jy = filter_year or cur_jy
        jm = filter_month or cur_jm
        start, end = jalali_month_bounds(jy, jm)
        label = f"{_jalali_month_name(jm)} {to_persian_digits(str(jy))}"
        is_current = jy == cur_jy and jm == cur_jm
        return start, end, label, is_current, jy, jm, True

    if mode == "range" and filter_start and filter_end:
        start = min(filter_start, filter_end)
        end = max(filter_start, filter_end)
        label = f"{_compact_jalali(start)} — {_compact_jalali(end)}"
        return start, end, label, False, cur_jy, cur_jm, True

    return None, None, "همه", False, cur_jy, cur_jm, False


def compute_streak(db: Database, today: datetime.date) -> int:
    streak = 0
    d = today
    while True:
        useful, _ = db.get_useful_totals(d)
        if useful > 0:
            streak += 1
            d -= datetime.timedelta(days=1)
        else:
            break
    return streak


def _project_dict(project: Project, db: Database) -> dict:
    stats = db.get_project_stats(project.id)
    dl = project.days_until_deadline()
    if dl is None:
        deadline_label = ""
    elif dl < 0:
        deadline_label = to_persian_digits(f"{abs(dl)} روز گذشته")
    elif dl == 0:
        deadline_label = "امروز"
    else:
        deadline_label = to_persian_digits(f"{dl} روز مانده")
    return {
        "id": project.id,
        "title": project.title,
        "color": project.color,
        "deadline": project.deadline or "",
        "deadline_label": deadline_label,
        "deadline_overdue": dl is not None and dl < 0,
        "is_done": project.is_done,
        "total": stats["total"],
        "done": stats["done"],
        "progress": stats["progress"],
    }


def _project_task_dict(task: ProjectTask, db: Database, today: datetime.date) -> dict:
    existing = db.get_daily_tasks_for_project_task(task.id)
    scheduled_today = any(t.date == today.isoformat() for t in existing)
    return {
        "id": task.id,
        "title": task.title,
        "is_done": task.is_done,
        "scheduled_today": scheduled_today,
    }


def _installment_dict(
    inst: Installment, db: Database, month_start: datetime.date, month_end: datetime.date
) -> dict:
    next_due = inst.next_due_date()
    today = datetime.date.today()
    if next_due is None:
        due_label = ""
        days_until = None
        is_overdue = False
    else:
        delta = (next_due - today).days
        days_until = delta
        is_overdue = delta < 0
        if delta < 0:
            due_label = to_persian_digits(f"{abs(delta)} روز گذشته")
        elif delta == 0:
            due_label = "امروز"
        else:
            due_label = to_persian_digits(f"{delta} روز مانده")

    progress = int(inst.paid_count / inst.total_count * 100) if inst.total_count else 0
    paid_month = db.is_paid_in_date_range(inst.id, month_start, month_end)

    return {
        "id": inst.id,
        "title": inst.title,
        "amount": inst.amount,
        "amount_fmt": format_money(inst.amount),
        "total_count": inst.total_count,
        "paid_count": inst.paid_count,
        "remaining_count": inst.remaining_count,
        "remaining_amount": inst.remaining_amount,
        "remaining_fmt": format_money(inst.remaining_amount),
        "progress": progress,
        "is_settled": inst.is_settled,
        "due_day": inst.due_day,
        "start_date": inst.start_date,
        "due_label": due_label,
        "is_overdue": is_overdue,
        "paid_this_month": paid_month,
    }


def _important_date_dict(item: ImportantDate, today: datetime.date) -> dict:
    days = item.days_until(today)
    if days < 0:
        urgency = "overdue"
        countdown = to_persian_digits(f"{abs(days)} روز گذشته")
    elif days == 0:
        urgency = "urgent"
        countdown = "امروز"
    elif days <= 7:
        urgency = "urgent"
        countdown = to_persian_digits(f"{days} روز مانده")
    elif days <= 30:
        urgency = "soon"
        countdown = to_persian_digits(f"{days} روز مانده")
    else:
        months = days // 30
        if months >= 2:
            countdown = to_persian_digits(f"{months} ماه مانده")
        else:
            countdown = to_persian_digits(f"{days} روز مانده")
        urgency = "ok"
    try:
        date_fmt = format_jalali(datetime.date.fromisoformat(item.date))
    except ValueError:
        date_fmt = item.date
    return {
        "id": item.id,
        "title": item.title,
        "date": item.date,
        "date_fmt": date_fmt,
        "category": item.category,
        "notes": item.notes,
        "repeat_type": item.repeat_type,
        "repeat_months": item.repeat_months,
        "days": days,
        "countdown": countdown,
        "urgency": urgency,
        "is_repeating": item.is_repeating,
    }


def build_state(
    db: Database,
    timer: TimerService,
    screen: str,
    current_date: datetime.date,
    expanded_tasks: Set[int],
    analytics_period: int,
    search_query: str = "",
    show_calendar: bool = False,
    calendar_year: Optional[int] = None,
    calendar_month: Optional[int] = None,
    finance_year: Optional[int] = None,
    finance_month: Optional[int] = None,
    invest_filter_mode: str = "all",
    invest_filter_year: Optional[int] = None,
    invest_filter_month: Optional[int] = None,
    invest_filter_start: Optional[datetime.date] = None,
    invest_filter_end: Optional[datetime.date] = None,
    toast: Optional[dict] = None,
    current_project_id: Optional[int] = None,
    export_path: str = "",
) -> dict:
    today = datetime.date.today()
    active_id = timer.active_task_id
    elapsed = timer.get_elapsed() if active_id else 0
    theme = db.get_setting("theme", "dark")

    categories = all_finance_categories(db)

    state: Dict[str, Any] = {
        "screen": screen,
        "theme": theme,
        "toast": toast,
        "mood_emojis": MOOD_EMOJIS,
        "finance_categories": categories,
        "investment_categories": _investment_categories_for_db(db),
        "investment_taxonomy": _investment_taxonomy_for_db(db),
    }

    if screen == "home":
        tasks = db.get_tasks_for_date(current_date)
        if search_query:
            q = search_query.strip().lower()
            tasks = [t for t in tasks if q in t.title.lower()]
        useful, not_useful = db.get_useful_totals(current_date)
        classified = useful + not_useful
        eff = int(useful / classified * 100) if classified > 0 else 0
        wellness = db.get_wellness(current_date)
        note = db.get_daily_note(current_date)

        jy, jm, _ = gregorian_to_jalali_parts(current_date)
        cal_y = calendar_year or jy
        cal_m = calendar_month or jm

        state["home"] = {
            "date": current_date.isoformat(),
            "date_label": format_jalali(current_date),
            "is_today": current_date == today,
            "search": search_query,
            "show_calendar": show_calendar,
            "calendar": build_calendar_month(cal_y, cal_m, db) if show_calendar else None,
            "useful": useful,
            "not_useful": not_useful,
            "useful_fmt": format_duration(useful),
            "not_useful_fmt": format_duration(not_useful),
            "efficiency": eff,
            "tasks": [_task_dict(t, expanded_tasks, active_id, elapsed) for t in tasks],
            "wellness": _wellness_dict(wellness),
            "daily_note": note or "",
            "recurring_count": len(db.get_all_recurring()),
            "urgent_dates_count": db.count_urgent_dates(today, threshold_days=7),
        }

    elif screen == "analytics":
        start = today - datetime.timedelta(days=analytics_period - 1)
        tasks_data = db.get_tasks_summary_for_range(start, today)
        finance_data = db.get_finance_summary_for_range(start, today)
        wellness_data = db.get_wellness_for_range(start, today)

        total = sum(d["total"] for d in tasks_data)
        useful = sum(d["useful"] for d in tasks_data)
        not_useful = sum(d["not_useful"] for d in tasks_data)
        classified = useful + not_useful
        eff = int(useful / classified * 100) if classified > 0 else 0
        income = finance_data["total_income"]
        expense = finance_data["total_expense"]
        investment = finance_data["total_investment"]

        moods = [w.mood_score for w in wellness_data if w.mood_score]
        avg_mood = f"{sum(moods)/len(moods):.1f}" if moods else DASH
        sleeps = [w.sleep_duration_minutes() for w in wellness_data if w.sleep_duration_minutes()]
        avg_sleep = format_sleep_duration(int(sum(sleeps)/len(sleeps))) if sleeps else DASH

        chart_points = []
        heatmap = []
        day_cards = []
        for d in tasks_data:
            day_str = d["date"]
            t_total = d["total"]
            t_useful = d["useful"]
            t_not_useful = d["not_useful"]
            t_classified = t_useful + t_not_useful
            t_eff = int(t_useful / t_classified * 100) if t_classified > 0 else 0
            chart_points.append(t_eff)
            heatmap.append({"date": day_str, "eff": t_eff, "total": t_total})
            w = next((x for x in wellness_data if x.date == day_str), None)
            day_cards.append({
                "date_label": _safe_jalali_label(day_str),
                "total_fmt": format_duration(t_total),
                "useful_fmt": format_duration(t_useful),
                "eff": t_eff,
                "mood": (
                    MOOD_EMOJIS[w.mood_score - 1]
                    if w and w.mood_score and 1 <= w.mood_score <= len(MOOD_EMOJIS)
                    else ""
                ),
                "sleep": format_sleep_duration(w.sleep_duration_minutes()) if w and w.sleep_duration_minutes() else "",
            })

        state["analytics"] = {
            "period": analytics_period,
            "start_label": format_jalali(start),
            "end_label": format_jalali(today),
            "stats": {
                "total_fmt": format_duration(total),
                "useful": useful,
                "not_useful": not_useful,
                "useful_fmt": format_duration(useful),
                "not_useful_fmt": format_duration(not_useful),
                "eff": eff,
                "income": income,
                "expense": expense,
                "income_fmt": format_money(income),
                "expense_fmt": format_money(expense),
                "investment_fmt": format_money(investment),
                "balance_fmt": format_money(income - expense - investment),
                "balance": income - expense - investment,
                "avg_mood": to_persian_digits(avg_mood),
                "avg_sleep": avg_sleep,
                "streak": compute_streak(db, today),
            },
            "chart_points": chart_points,
            "heatmap": heatmap,
            "days": list(reversed(day_cards)),
        }

    elif screen == "finance":
        cur_jy, cur_jm = current_jalali_ym(today)
        jy = finance_year or cur_jy
        jm = finance_month or cur_jm
        month_start, month_end = jalali_month_bounds(jy, jm)
        month_label = f"{_jalali_month_name(jm)} {to_persian_digits(str(jy))}"

        monthly_totals = db.get_finance_monthly_totals_between(month_start, month_end)
        budget_limits = db.get_budget_limits()
        income = monthly_totals["total_income"]
        expense = monthly_totals["total_expense"]
        investment = monthly_totals["total_investment"]
        balance = income - expense - investment

        by_cat_data = dict(monthly_totals["by_category"])
        for cat in categories:
            if cat not in by_cat_data:
                by_cat_data[cat] = {"income": 0, "expense": 0, "investment": 0}
        for cat in budget_limits:
            if cat not in by_cat_data:
                by_cat_data[cat] = {"income": 0, "expense": 0, "investment": 0}

        by_category_list = []
        custom_cats = set(db.get_finance_custom_categories())
        for cat, amounts in by_cat_data.items():
            cat_income = amounts["income"]
            cat_expense = amounts["expense"]
            cat_investment = amounts["investment"]
            budget = budget_limits.get(cat, 0)
            if cat in BUDGET_EXCLUDED_CATEGORIES and budget <= 0:
                continue
            if cat_expense <= 0 and budget <= 0:
                if cat not in custom_cats:
                    continue
                if cat_income > 0 or cat_investment > 0:
                    continue
            by_category_list.append({
                "category": cat,
                "income": cat_income,
                "expense": cat_expense,
                "income_fmt": format_money(cat_income),
                "expense_fmt": format_money(cat_expense),
                "budget": budget,
                "budget_fmt": format_money(budget),
                "used_pct": int(cat_expense / budget * 100) if budget > 0 else 0,
                "over_budget": budget > 0 and cat_expense > budget,
            })
        by_category_list.sort(key=lambda x: x["expense"], reverse=True)

        daily_series = []
        for row in reversed(db.get_finance_daily_series_between(month_start, month_end)):
            day_income = row["income"]
            day_expense = row["expense"]
            day_investment = row["investment"]
            net = day_income - day_expense - day_investment
            daily_series.append({
                "date_label": _safe_jalali_label(row["date"]),
                "income_fmt": format_money(day_income),
                "expense_fmt": format_money(day_expense),
                "investment_fmt": format_money(day_investment),
                "income": day_income,
                "expense": day_expense,
                "investment": day_investment,
                "net": net,
                "net_fmt": format_money(net),
            })

        daily_raw = {
            row["date"]: row for row in db.get_finance_daily_series_between(month_start, month_end)
        }
        chart_income: List[int] = []
        chart_expense: List[int] = []
        chart_investment: List[int] = []
        chart_balance: List[int] = []
        chart_labels: List[str] = []
        cum_income = 0
        cum_expense = 0
        cum_investment = 0
        chart_day = month_start
        while chart_day <= month_end:
            row = daily_raw.get(chart_day.isoformat(), {"income": 0, "expense": 0, "investment": 0})
            cum_income += int(row["income"])
            cum_expense += int(row["expense"])
            cum_investment += int(row["investment"])
            chart_income.append(cum_income)
            chart_expense.append(cum_expense)
            chart_investment.append(cum_investment)
            chart_balance.append(cum_income - cum_expense - cum_investment)
            jd = jdatetime.date.fromgregorian(date=chart_day)
            chart_labels.append(to_persian_digits(str(jd.day)))
            chart_day += datetime.timedelta(days=1)

        entries = db.get_finance_entries_between(month_start, month_end)

        inst_summary = db.get_installments_summary_for_range(month_start, month_end)

        state["finance_screen"] = {
            "year": jy,
            "month": jm,
            "month_label": month_label,
            "is_current_month": jy == cur_jy and jm == cur_jm,
            "totals": {
                "income": income,
                "expense": expense,
                "investment": investment,
                "balance": balance,
                "income_fmt": format_money(income),
                "expense_fmt": format_money(expense),
                "investment_fmt": format_money(investment),
                "balance_fmt": format_money(balance),
            },
            "by_category": by_category_list,
            "daily_series": daily_series,
            "chart": {
                "labels": chart_labels,
                "income": chart_income,
                "expense": chart_expense,
                "investment": chart_investment,
                "balance": chart_balance,
                "has_data": income > 0 or expense > 0 or investment > 0,
            },
            "entries": [_finance_dict_with_date(e) for e in entries],
            "finance_categories": categories,
            "investment_categories": _investment_categories_for_db(db),
            "investment_taxonomy": _investment_taxonomy_for_db(db),
            "budgets": budget_limits,
            "installments": {
                "count": len(inst_summary["items"]),
                "total_due_fmt": format_money(inst_summary["total_due"]),
                "total_unpaid_fmt": format_money(inst_summary["total_unpaid"]),
                "items": [
                    _installment_dict(x["installment"], db, month_start, month_end)
                    for x in inst_summary["items"]
                ],
            },
        }

    elif screen == "installments":
        cur_jy, cur_jm = current_jalali_ym(today)
        jy = finance_year or cur_jy
        jm = finance_month or cur_jm
        month_start, month_end = jalali_month_bounds(jy, jm)
        month_label = f"{_jalali_month_name(jm)} {to_persian_digits(str(jy))}"

        installments = db.get_all_installments()
        summary = db.get_installments_summary_for_range(month_start, month_end)
        total_remaining = sum(i.remaining_amount for i in installments if not i.is_settled)

        state["installments"] = {
            "list": [
                _installment_dict(i, db, month_start, month_end) for i in installments
            ],
            "month_label": month_label,
            "month_total_due": summary["total_due"],
            "month_total_unpaid": summary["total_unpaid"],
            "month_total_due_fmt": format_money(summary["total_due"]),
            "month_total_unpaid_fmt": format_money(summary["total_unpaid"]),
            "total_remaining_fmt": format_money(total_remaining),
        }

    elif screen == "investments":
        as_of = today
        balance = db.get_finance_balance_until(as_of)
        portfolio_total = db.get_total_investment_until(as_of)

        (
            period_start,
            period_end,
            filter_label,
            is_current_month,
            goal_jy,
            goal_jm,
            bounded,
        ) = _resolve_invest_filter_bounds(
            invest_filter_mode,
            invest_filter_year,
            invest_filter_month,
            invest_filter_start,
            invest_filter_end,
            today,
        )

        if bounded and period_start and period_end:
            entries = db.get_investment_entries_between(period_start, period_end)
            monthly_totals = db.get_finance_monthly_totals_between(
                period_start, period_end
            )
            period_investment = monthly_totals["total_investment"]
        else:
            entries = db.get_all_investment_entries()
            period_investment = portfolio_total

        goal = db.get_investment_goal(goal_jy, goal_jm) if invest_filter_mode == "month" else 0

        by_asset: Dict[str, int] = {}
        for entry in entries:
            key = investment_group_key(entry.category or "")
            by_asset[key] = by_asset.get(key, 0) + entry.signed_amount
        by_category_list = _category_breakdown_list(by_asset, period_investment)

        portfolio_entries = db.get_investment_entries_until(as_of)
        asset_prices = merge_asset_prices(
            db.get_investment_asset_prices(), portfolio_entries
        )
        positions_raw = compute_positions(portfolio_entries, asset_prices)
        positions = [_position_dict(p) for p in positions_raw]
        estimated_total = sum(p["estimated_value"] for p in positions)
        has_market_values = any(p["has_market_price"] for p in positions)
        total_unrealized_pnl = None
        if has_market_values:
            total_unrealized_pnl = sum(
                p.get("unrealized_pnl") or 0 for p in positions_raw
            )

        breakdown = portfolio_breakdown(portfolio_entries)
        value_breakdown = positions_value_breakdown(positions_raw)
        portfolio_by_category = _category_breakdown_list(
            value_breakdown["by_asset"] if positions else breakdown["by_asset"],
            estimated_total if has_market_values else portfolio_total,
        )
        portfolio_by_risk = _category_breakdown_list(
            value_breakdown["by_risk"] if positions else breakdown["by_risk"],
            estimated_total if has_market_values else portfolio_total,
        )

        period_buys = period_buy_total(entries)

        chart_investment: List[int] = []
        chart_portfolio: List[int] = []
        chart_labels: List[str] = []
        has_chart = False
        if bounded and period_start and period_end:
            daily_raw = {
                row["date"]: row
                for row in db.get_finance_daily_series_between(period_start, period_end)
            }
            portfolio_before = db.get_total_investment_until(
                period_start - datetime.timedelta(days=1)
            )
            cum_period = 0
            chart_day = period_start
            while chart_day <= period_end:
                row = daily_raw.get(
                    chart_day.isoformat(), {"income": 0, "expense": 0, "investment": 0}
                )
                cum_period += int(row["investment"])
                chart_investment.append(cum_period)
                chart_portfolio.append(portfolio_before + cum_period)
                jd = jdatetime.date.fromgregorian(date=chart_day)
                chart_labels.append(to_persian_digits(str(jd.day)))
                chart_day += datetime.timedelta(days=1)
            has_chart = any(chart_investment)

        inv_taxonomy = _investment_taxonomy_for_db(db)
        cur_jy, cur_jm = current_jalali_ym(today)
        period_stat_label = "در بازه" if bounded else "کل"
        all_entries = [
            _finance_dict_with_date(e) for e in db.get_investment_entries_until(as_of)
        ]
        custom_assets = db.get_investment_custom_assets()
        allocation_targets_raw = db.get_investment_allocation_targets()
        allocation_items = compute_allocation_comparison(positions_raw, allocation_targets_raw)
        allocation_list = []
        for item in allocation_items:
            allocation_list.append({
                **item,
                "actual_value_fmt": format_money(item["actual_value"]),
                "drift_fmt": (
                    f"{'+' if item['drift'] > 0 else ''}{to_persian_digits(str(item['drift']))}٪"
                    if item.get("target_pct")
                    else ""
                ),
                "over_target": item.get("drift", 0) > 1,
                "under_target": item.get("target_pct", 0) > 0 and item.get("drift", 0) < -1,
            })
        targets_total = allocation_targets_total(allocation_targets_raw)
        prices_synced_at = db.get_investment_prices_synced_at()

        state["investments"] = {
            "filter": {
                "mode": invest_filter_mode,
                "label": filter_label,
                "year": invest_filter_year or cur_jy,
                "month": invest_filter_month or cur_jm,
                "start": period_start.isoformat() if period_start else "",
                "end": period_end.isoformat() if period_end else "",
                "is_current_month": is_current_month,
                "period_stat_label": period_stat_label,
            },
            "totals": {
                "balance": balance,
                "balance_fmt": format_money(balance),
                "period_investment": period_investment,
                "period_investment_fmt": format_money(abs(period_investment)),
                "period_buys": period_buys,
                "period_buys_fmt": format_money(period_buys),
                "month_investment": period_investment,
                "month_investment_fmt": format_money(abs(period_investment)),
                "net_invested": portfolio_total,
                "net_invested_fmt": format_money(abs(portfolio_total)),
                "portfolio_total": portfolio_total,
                "portfolio_total_fmt": format_money(abs(portfolio_total)),
                "estimated_value": estimated_total,
                "estimated_value_fmt": format_money(estimated_total),
                "has_market_values": has_market_values,
                "unrealized_pnl": total_unrealized_pnl,
                "unrealized_pnl_fmt": (
                    format_money(abs(total_unrealized_pnl))
                    if total_unrealized_pnl is not None
                    else ""
                ),
                "unrealized_pnl_positive": (
                    total_unrealized_pnl is not None and total_unrealized_pnl >= 0
                ),
            },
            "positions": positions,
            "goal": goal,
            "goal_fmt": format_money(goal) if goal > 0 else "",
            "goal_pct": int(period_buys / goal * 100) if goal > 0 else 0,
            "over_goal": goal > 0 and period_buys > goal,
            "by_category": by_category_list,
            "portfolio_by_category": portfolio_by_category,
            "portfolio_by_risk": portfolio_by_risk,
            "entries": [_finance_dict_with_date(e) for e in entries],
            "all_entries": all_entries,
            "chart": {
                "labels": chart_labels,
                "investment": chart_investment,
                "portfolio": chart_portfolio,
                "has_data": has_chart,
            },
            "investment_categories": _investment_categories_for_db(db),
            "investment_taxonomy": inv_taxonomy,
            "custom_assets": custom_assets,
            "allocation": allocation_list,
            "allocation_targets_total": targets_total,
            "allocation_targets_valid": targets_total <= 100,
            "prices_synced_at": prices_synced_at,
        }

    elif screen == "settings":
        state["settings"] = {
            "theme": theme,
            "export_path": export_path,
            "backup_summary": db.get_backup_summary(),
        }

    elif screen == "recurring":
        state["recurring"] = [
            {"id": r.id, "title": r.title}
            for r in db.get_all_recurring()
        ]

    elif screen == "projects":
        projects = db.get_all_projects()
        state["projects"] = {
            "list": [_project_dict(p, db) for p in projects],
            "colors": PROJECT_COLORS,
        }

    elif screen == "project_detail":
        project = db.get_project_by_id(current_project_id) if current_project_id else None
        if project:
            tasks = db.get_project_tasks(project.id)
            state["project_detail"] = {
                **_project_dict(project, db),
                "tasks": [_project_task_dict(t, db, today) for t in tasks],
                "colors": PROJECT_COLORS,
            }

    elif screen == "important_dates":
        items = db.get_all_important_dates()
        dicts = [_important_date_dict(i, today) for i in items]
        dicts.sort(key=lambda x: x["days"])

        state["important_dates"] = {
            "items": dicts,
            "categories": IMPORTANT_DATE_CATEGORIES,
            "urgent_count": sum(
                1 for d in dicts if d["urgency"] in ("overdue", "urgent")
            ),
        }

    elif screen == "tracking":
        from datetime import datetime as _dt

        def _epoch_to_hhmm(epoch):
            if epoch is None:
                return None
            t = _dt.fromtimestamp(epoch)
            return to_persian_digits(f"{t.hour:02d}:{t.minute:02d}")

        def _fmt_dur(secs):
            if secs is None:
                return None
            h = secs // 3600
            m = (secs % 3600) // 60
            s = secs % 60
            if h > 0:
                return to_persian_digits(f"{h}:{m:02d}:{s:02d}")
            return to_persian_digits(f"{m:02d}:{s:02d}")

        track_date = today
        db.close_stale_tracking_sessions(track_date)
        sessions = db.get_tracking_sessions_for_date(track_date)
        active_row = db.get_active_tracking_session(track_date)

        all_intervals_out: List[dict] = []
        earlier_intervals_out: List[dict] = []
        day_total_secs = 0
        useful_secs = 0
        not_useful_secs = 0
        completed_count = 0
        by_label: dict = {}
        active_session_out = None

        for sess in sessions:
            rows = db.get_tracking_intervals(sess["id"])
            sess_completed_secs = 0
            for r in rows:
                is_active = r["ended_at"] is None
                dur = r["duration_secs"] or 0
                raw_useful = r["is_useful"] if "is_useful" in r.keys() else None
                is_useful = None if raw_useful is None else bool(raw_useful)
                iv = {
                    "id": r["id"],
                    "session_id": sess["id"],
                    "label": r["label"],
                    "started_label": _epoch_to_hhmm(r["started_at"]),
                    "ended_label": _epoch_to_hhmm(r["ended_at"]),
                    "duration_label": _fmt_dur(dur if dur else None),
                    "duration_secs": dur if not is_active else 0,
                    "started_epoch": r["started_at"],
                    "is_active": is_active,
                    "is_useful": is_useful,
                }
                all_intervals_out.append(iv)
                if not is_active and dur:
                    day_total_secs += dur
                    completed_count += 1
                    sess_completed_secs += dur
                    if is_useful is True:
                        useful_secs += dur
                    elif is_useful is False:
                        not_useful_secs += dur
                    lbl = (r["label"] or "").strip() or "بدون عنوان"
                    by_label[lbl] = by_label.get(lbl, 0) + dur

            if active_row and sess["id"] == active_row["id"]:
                active_session_out = {
                    "id": sess["id"],
                    "is_active": True,
                    "started_label": _epoch_to_hhmm(sess["started_at"]),
                    "ended_label": None,
                    "total_label": _fmt_dur(sess_completed_secs),
                    "total_secs": sess_completed_secs,
                }

        breakdown_out = []
        for lbl, secs in sorted(by_label.items(), key=lambda x: -x[1]):
            pct = int(secs / day_total_secs * 100) if day_total_secs else 0
            breakdown_out.append({
                "label": lbl,
                "duration_secs": secs,
                "duration_label": _fmt_dur(secs),
                "pct": pct,
            })

        if active_row:
            active_sid = active_row["id"]
            earlier_intervals_out = [
                iv for iv in all_intervals_out
                if iv["session_id"] != active_sid and not iv["is_active"]
            ]

        classified = useful_secs + not_useful_secs
        efficiency = int(useful_secs / classified * 100) if classified > 0 else None

        state["tracking"] = {
            "date_label": format_jalali(track_date),
            "has_data": len(sessions) > 0,
            "session": active_session_out,
            "intervals": all_intervals_out,
            "earlier_intervals": earlier_intervals_out,
            "breakdown": breakdown_out,
            "day_total_label": _fmt_dur(day_total_secs),
            "day_total_secs": day_total_secs,
            "useful_label": _fmt_dur(useful_secs) if useful_secs else None,
            "not_useful_label": _fmt_dur(not_useful_secs) if not_useful_secs else None,
            "efficiency": efficiency,
            "completed_count": completed_count,
            "session_count": len(sessions),
        }

    return state
