"""Build JSON state for the SPA WebView client."""
import datetime
from typing import Any, Dict, List, Optional, Set

import jdatetime

from dailyplanner.database import Database
from dailyplanner.models import (
    DailyTask,
    DailyWellness,
    FinanceEntry,
    format_clock_time,
    format_duration,
    format_money,
    format_sleep_duration,
    str_to_date,
)
from dailyplanner.services.timer import TimerService
from dailyplanner.ui.tokens import FINANCE_CATEGORIES, MOOD_EMOJIS
from dailyplanner.utils.jalali import (
    format_jalali,
    gregorian_to_jalali_parts,
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


def _finance_dict(entry: FinanceEntry) -> dict:
    return {
        "id": entry.id,
        "title": entry.title,
        "amount": entry.amount,
        "amount_fmt": format_money(entry.amount),
        "type": entry.entry_type,
        "category": entry.category or "عمومی",
    }


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


def build_calendar_month(year: int, month: int, db: Database) -> dict:
    jd = jdatetime.date(year, month, 1)
    days_in_month = jdatetime.j_days_in_month[month - 1]
    if month == 12 and jd.isleap():
        days_in_month = 30
    cells = []
    for day in range(1, days_in_month + 1):
        g = jalali_to_gregorian(year, month, day)
        useful, not_useful = db.get_useful_totals(g)
        total = useful + not_useful
        eff = int(useful / total * 100) if total > 0 else 0
        cells.append({
            "day": day,
            "date": g.isoformat(),
            "eff": eff,
            "has_data": total > 0,
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
    toast: Optional[dict] = None,
) -> dict:
    today = datetime.date.today()
    active_id = timer.active_task_id
    elapsed = timer.get_elapsed() if active_id else 0
    theme = db.get_setting("theme", "dark")

    state: Dict[str, Any] = {
        "screen": screen,
        "theme": theme,
        "toast": toast,
        "mood_emojis": MOOD_EMOJIS,
        "finance_categories": FINANCE_CATEGORIES,
    }

    if screen == "home":
        tasks = db.get_tasks_for_date(current_date)
        if search_query:
            q = search_query.strip().lower()
            tasks = [t for t in tasks if q in t.title.lower()]
        useful, not_useful = db.get_useful_totals(current_date)
        total = useful + not_useful
        eff = int(useful / total * 100) if total > 0 else 0
        entries = db.get_finance_entries_for_date(current_date)
        income, expense = db.get_finance_daily_totals(current_date)
        balance = db.get_finance_balance_until(current_date)
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
            "finance": {
                "entries": [_finance_dict(e) for e in entries],
                "income": income,
                "expense": expense,
                "balance": balance,
                "income_fmt": format_money(income),
                "expense_fmt": format_money(expense),
                "balance_fmt": format_money(balance),
            },
            "wellness": _wellness_dict(wellness),
            "daily_note": note or "",
            "recurring_count": len(db.get_all_recurring()),
        }

    elif screen == "analytics":
        start = today - datetime.timedelta(days=analytics_period - 1)
        tasks_data = db.get_tasks_summary_for_range(start, today)
        finance_data = db.get_finance_summary_for_range(start, today)
        wellness_data = db.get_wellness_for_range(start, today)

        total = sum(d["total"] for d in tasks_data)
        useful = sum(d["useful"] for d in tasks_data)
        not_useful = sum(d["not_useful"] for d in tasks_data)
        eff = int(useful / total * 100) if total > 0 else 0
        income = finance_data["total_income"]
        expense = finance_data["total_expense"]

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
            t_eff = int(t_useful / t_total * 100) if t_total > 0 else 0
            chart_points.append(t_eff)
            heatmap.append({"date": day_str, "eff": t_eff, "total": t_total})
            gdate = str_to_date(day_str)
            w = next((x for x in wellness_data if x.date == day_str), None)
            day_cards.append({
                "date_label": format_jalali(gdate),
                "total_fmt": format_duration(t_total),
                "useful_fmt": format_duration(t_useful),
                "eff": t_eff,
                "mood": MOOD_EMOJIS[w.mood_score - 1] if w and w.mood_score else "",
                "sleep": format_sleep_duration(w.sleep_duration_minutes()) if w and w.sleep_duration_minutes() else "",
            })

        state["analytics"] = {
            "period": analytics_period,
            "start_label": format_jalali(start),
            "end_label": format_jalali(today),
            "stats": {
                "total_fmt": format_duration(total),
                "useful_fmt": format_duration(useful),
                "not_useful_fmt": format_duration(not_useful),
                "eff": eff,
                "income_fmt": format_money(income),
                "expense_fmt": format_money(expense),
                "balance_fmt": format_money(income - expense),
                "avg_mood": to_persian_digits(avg_mood),
                "avg_sleep": avg_sleep,
                "streak": compute_streak(db, today),
            },
            "chart_points": chart_points,
            "heatmap": heatmap,
            "days": list(reversed(day_cards)),
        }

    elif screen == "settings":
        state["settings"] = {
            "theme": theme,
            "export_ready": True,
        }

    elif screen == "recurring":
        state["recurring"] = [
            {"id": r.id, "title": r.title}
            for r in db.get_all_recurring()
        ]

    return state
