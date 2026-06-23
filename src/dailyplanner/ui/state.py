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
from dailyplanner.ui.tokens import (
    BUDGET_EXCLUDED_CATEGORIES,
    FINANCE_CATEGORIES,
    IMPORTANT_DATE_CATEGORIES,
    INVESTMENT_CATEGORIES,
    MOOD_EMOJIS,
    PROJECT_COLORS,
)
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


def _finance_dict_with_date(entry: FinanceEntry) -> dict:
    d = _finance_dict(entry)
    d["date"] = entry.date
    d["date_label"] = format_jalali(str_to_date(entry.date))
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


def _installment_dict(inst: Installment, db: Database, year: int, month: int) -> dict:
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
    paid_month = db.is_paid_this_month(inst.id, year, month)

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
    return {
        "id": item.id,
        "title": item.title,
        "date": item.date,
        "date_fmt": format_jalali(datetime.date.fromisoformat(item.date)),
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
        "investment_categories": INVESTMENT_CATEGORIES,
    }

    if screen == "home":
        tasks = db.get_tasks_for_date(current_date)
        if search_query:
            q = search_query.strip().lower()
            tasks = [t for t in tasks if q in t.title.lower()]
        useful, not_useful = db.get_useful_totals(current_date)
        total = useful + not_useful
        eff = int(useful / total * 100) if total > 0 else 0
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
        eff = int(useful / total * 100) if total > 0 else 0
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
                "investment_fmt": format_money(investment),
                "balance_fmt": format_money(income - expense - investment),
                "avg_mood": to_persian_digits(avg_mood),
                "avg_sleep": avg_sleep,
                "streak": compute_streak(db, today),
            },
            "chart_points": chart_points,
            "heatmap": heatmap,
            "days": list(reversed(day_cards)),
        }

    elif screen == "finance":
        fy = finance_year or today.year
        fm = finance_month or today.month
        first_day = datetime.date(fy, fm, 1)
        jy, jm, _ = gregorian_to_jalali_parts(first_day)
        month_label = f"{_jalali_month_name(jm)} {to_persian_digits(str(jy))}"

        monthly_totals = db.get_finance_monthly_totals(fy, fm)
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
        for row in reversed(db.get_finance_daily_series(fy, fm)):
            g_date = str_to_date(row["date"])
            day_income = row["income"]
            day_expense = row["expense"]
            day_investment = row["investment"]
            net = day_income - day_expense - day_investment
            daily_series.append({
                "date_label": format_jalali(g_date),
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
            row["date"]: row for row in db.get_finance_daily_series(fy, fm)
        }
        last_day = calendar.monthrange(fy, fm)[1]
        chart_income: List[int] = []
        chart_expense: List[int] = []
        chart_investment: List[int] = []
        chart_balance: List[int] = []
        chart_labels: List[str] = []
        cum_income = 0
        cum_expense = 0
        cum_investment = 0
        for day in range(1, last_day + 1):
            d = datetime.date(fy, fm, day)
            row = daily_raw.get(d.isoformat(), {"income": 0, "expense": 0, "investment": 0})
            cum_income += int(row["income"])
            cum_expense += int(row["expense"])
            cum_investment += int(row["investment"])
            chart_income.append(cum_income)
            chart_expense.append(cum_expense)
            chart_investment.append(cum_investment)
            chart_balance.append(cum_income - cum_expense - cum_investment)
            chart_labels.append(to_persian_digits(str(day)))

        entries = db.get_finance_entries_for_month(fy, fm)

        inst_summary = db.get_installments_summary_for_month(fy, fm)

        state["finance_screen"] = {
            "year": fy,
            "month": fm,
            "month_label": month_label,
            "is_current_month": fy == today.year and fm == today.month,
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
            "investment_categories": INVESTMENT_CATEGORIES,
            "budgets": budget_limits,
            "installments": {
                "count": len(inst_summary["items"]),
                "total_due_fmt": format_money(inst_summary["total_due"]),
                "total_unpaid_fmt": format_money(inst_summary["total_unpaid"]),
                "items": [
                    {
                        "id": x["installment"].id,
                        "title": x["installment"].title,
                        "amount_fmt": format_money(x["installment"].amount),
                        "paid_this_month": x["paid_this_month"],
                        "is_settled": x["installment"].is_settled,
                    }
                    for x in inst_summary["items"]
                ],
            },
        }

    elif screen == "installments":
        fy = finance_year or today.year
        fm = finance_month or today.month
        first_day = datetime.date(fy, fm, 1)
        jy, jm, _ = gregorian_to_jalali_parts(first_day)
        month_label = f"{_jalali_month_name(jm)} {to_persian_digits(str(jy))}"

        installments = db.get_all_installments()
        summary = db.get_installments_summary_for_month(fy, fm)
        total_remaining = sum(i.remaining_amount for i in installments if not i.is_settled)

        state["installments"] = {
            "list": [
                _installment_dict(i, db, fy, fm) for i in installments
            ],
            "month_label": month_label,
            "month_total_due": summary["total_due"],
            "month_total_unpaid": summary["total_unpaid"],
            "month_total_due_fmt": format_money(summary["total_due"]),
            "month_total_unpaid_fmt": format_money(summary["total_unpaid"]),
            "total_remaining_fmt": format_money(total_remaining),
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

    return state
