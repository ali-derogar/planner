"""Tests for Daily Planner."""
import datetime
import tempfile
from pathlib import Path

import pytest

from dailyplanner.database import Database
from dailyplanner.models import str_to_date
from dailyplanner.services.recurring import RecurringService
from dailyplanner.services.timer import TimerService
from dailyplanner.ui.state import build_state, compute_streak


@pytest.fixture
def db():
    with tempfile.TemporaryDirectory() as tmp:
        database = Database(str(Path(tmp) / "test.db"))
        yield database
        database.close()


def test_add_task_and_duration(db):
    d = datetime.date.today()
    task = db.add_task(d, "??????")
    db.add_duration(task.id, 3600)
    updated = db.get_task_by_id(task.id)
    assert updated.duration_seconds == 3600


def test_finance_with_category(db):
    d = datetime.date.today()
    entry = db.add_finance_entry(d, "expense", "?????", 50000, "???")
    assert entry.category == "???"
    db.update_finance_entry(entry.id, "???", 60000, "expense", "???")
    updated = db.get_finance_entry_by_id(entry.id)
    assert updated.title == "???"
    assert updated.amount == 60000


def test_finance_investment_not_expense(db):
    d = datetime.date.today()
    db.add_finance_entry(d, "income", "salary", 1000000, "عمومی")
    db.add_finance_entry(d, "expense", "food", 100000, "غذا")
    db.add_finance_entry(d, "investment", "stocks", 200000, "سهام")

    income, expense, investment = db.get_finance_daily_totals(d)
    assert income == 1000000
    assert expense == 100000
    assert investment == 200000
    assert db.get_finance_balance_until(d) == 700000

    monthly = db.get_finance_monthly_totals(d.year, d.month)
    assert monthly["total_investment"] == 200000
    assert monthly["total_expense"] == 100000
    assert monthly["by_category"]["غذا"]["expense"] == 100000
    assert monthly["by_category"]["سهام"]["investment"] == 200000
    assert "expense" not in monthly["by_category"].get("سهام", {}) or monthly["by_category"]["سهام"]["expense"] == 0


def test_daily_note(db):
    d = datetime.date.today()
    db.set_daily_note(d, "??????? ???")
    assert db.get_daily_note(d) == "??????? ???"


def test_settings(db):
    db.set_setting("theme", "light")
    assert db.get_setting("theme") == "light"


def test_copy_task_to_next_day(db):
    d = datetime.date(2026, 6, 20)
    task = db.add_task(d, "????")
    db.update_estimated(task.id, 1800)
    new_task = db.copy_task_to_next_day(task.id)
    assert new_task is not None
    assert new_task.date == "2026-06-21"
    assert new_task.estimated_seconds == 1800


def test_move_task(db):
    d = datetime.date.today()
    t1 = db.add_task(d, "???")
    t2 = db.add_task(d, "???")
    db.move_task(t2.id, "up")
    tasks = db.get_tasks_for_date(d)
    assert tasks[0].id == t2.id


def test_recurring_service(db):
    svc = RecurringService(db)
    d = datetime.date.today()
    task = db.add_task(d, "??????")
    svc.star_task(task.id, task.title)
    updated = db.get_task_by_id(task.id)
    assert updated.is_starred


def test_timer_service():
    timer = TimerService()
    timer.start(1)
    assert timer.active_task_id == 1
    stopped, elapsed = timer.stop()
    assert stopped == 1
    assert elapsed >= 0


def test_timer_service_restore():
    import time

    timer = TimerService()
    started_at = time.time() - 120
    timer.restore(5, started_at)
    assert timer.active_task_id == 5
    assert timer.get_elapsed() >= 120


def test_active_timer_persistence(db):
    db.set_active_timer(42, 1700000000.5)
    active = db.get_active_timer()
    assert active == (42, 1700000000.5)
    db.clear_active_timer()
    assert db.get_active_timer() is None


def test_restore_active_timer_skips_missing_task(db):
    from dailyplanner.webview_handler import WebViewHandler

    class _App:
        pass

    db.set_active_timer(9999, 1700000000.0)
    app = _App()
    app.db = db
    handler = WebViewHandler(app)
    assert handler.timer_service.active_task_id is None
    assert db.get_active_timer() is None


def test_build_state_home(db):
    d = datetime.date.today()
    db.add_task(d, "???")
    timer = TimerService()
    state = build_state(
        db=db,
        timer=timer,
        screen="home",
        current_date=d,
        expanded_tasks=set(),
        analytics_period=7,
    )
    assert state["screen"] == "home"
    assert len(state["home"]["tasks"]) == 1


def test_compute_streak(db):
    today = datetime.date.today()
    task = db.add_task(today, "work")
    db.set_useful(task.id, True)
    db.add_duration(task.id, 600)
    streak = compute_streak(db, today)
    assert streak >= 1


def test_export_json(db):
    d = datetime.date.today()
    db.add_task(d, "???")
    data = db.export_json()
    assert "tasks" in data
    assert len(data["tasks"]) >= 1
    assert "installments" in data
    assert "installment_payments" in data


def test_backup_v1_installments_import(db):
    d = datetime.date.today()
    db.add_installment("loan", 500000, 12, d.isoformat(), 5)
    exported = db.export_json()
    exported["version"] = 1
    ok, err = db.validate_backup(exported)
    assert ok, err
    db.import_json(exported)
    assert len(db.get_all_installments()) == 1
    assert db.get_all_installments()[0].title == "loan"


def test_backup_roundtrip(db):
    d = datetime.date.today()
    db.add_task(d, "task-a")
    db.add_finance_entry(d, "expense", "coffee", 50000, "عمومی")
    db.add_finance_entry(d, "investment", "gold", 1000000, "سهام")
    db.add_installment("loan", 500000, 12, d.isoformat(), 5)
    db.add_important_date("birthday", d.isoformat(), "personal", "", "none", 0)

    exported = db.export_json()
    ok, err = db.validate_backup(exported)
    assert ok, err

    db.add_task(d, "task-b")
    db.import_json(exported)

    assert len(db.get_tasks_for_date(d)) == 1
    assert db.get_tasks_for_date(d)[0].title == "task-a"
    finance = db.get_finance_entries_for_month(d.year, d.month)
    assert len(finance) == 2
    assert db.get_all_installments()[0].title == "loan"
    assert len(db.get_all_important_dates()) == 1


def test_validate_backup_accepts_investment():
    from dailyplanner.database import Database

    db = Database(":memory:")
    data = db.export_json()
    data["finance"] = [{
        "id": 1,
        "date": "2026-06-22",
        "entry_type": "investment",
        "title": "gold",
        "amount": 1000,
        "category": "عمومی",
    }]
    ok, err = db.validate_backup(data)
    assert ok, err


def test_str_to_date():
    assert str_to_date("2026-06-22") == datetime.date(2026, 6, 22)


def test_parse_bank_sms_expense():
    from dailyplanner.finance_sms import parse_bank_sms, resolve_amount

    sms = """777.888.18007694.1
-2,700,000
04/01_21:44
مانده: 311,766,555"""
    parsed = parse_bank_sms(sms)
    assert parsed.amount == 270000
    assert parsed.direction == "expense"
    assert resolve_amount("", sms) == 270000


def test_parse_bank_sms_income():
    from dailyplanner.finance_sms import parse_bank_sms

    sms = """777.888.18007694.1
+270,000,000
04/01_18:30
مانده: 314,466,555"""
    parsed = parse_bank_sms(sms)
    assert parsed.amount == 27000000
    assert parsed.direction == "income"


def test_parse_bank_sms_samples():
    from dailyplanner.finance_sms import parse_bank_sms

    samples = [
        ("-509,000", 50900),
        ("-200,000", 20000),
        ("-3,560,000", 356000),
        ("-2,737,130", 273713),
    ]
    for line, expected in samples:
        sms = "777.888.18007694.1\n" + line + "\n03/31_15:19\nمانده: 48,735,555"
        assert parse_bank_sms(sms).amount == expected


def test_parse_bank_sms_ignores_balance_line():
    from dailyplanner.finance_sms import parse_bank_sms

    sms = "مانده: 311,766,555"
    assert parse_bank_sms(sms).amount == 0


def test_resolve_amount_persian_digits():
    from dailyplanner.finance_sms import resolve_amount, normalize_digits

    assert resolve_amount("۵۰۰۰۰", "") == 50000
    assert resolve_amount("۱۲،۳۴۵", "") == 12345
    assert normalize_digits(0) == "0"
    assert normalize_digits(None) == ""


def test_param_int_parsing():
    from dailyplanner.webview_handler import _param_int

    assert _param_int({}, "id") is None
    assert _param_int({"id": ""}, "id") is None
    assert _param_int({"id": "۱۲۳"}, "id") == 123
    assert _param_int({"total_count": "۱۲،۳"}, "total_count", 1) == 123
    assert _param_int({"due_day": "abc"}, "due_day", 1) is None
    assert _param_int({}, "days", 7) == 7
    assert _param_int({}, "repeat_months", 0) == 0


def test_parse_bank_sms_persian_comma_amount_line():
    from dailyplanner.finance_sms import parse_bank_sms

    sms = "777.888.18007694.1\n- ۲،۷۰۰،۰۰۰\n03/31_15:19"
    assert parse_bank_sms(sms).amount == 270000
    assert parse_bank_sms(sms).direction == "expense"


def test_build_state_all_screens(db):
    """Every SPA screen should produce renderable state."""
    import datetime

    today = datetime.date.today()
    db.add_task(today, "task")
    db.add_finance_entry(today, "expense", "x", 1000, "عمومی")
    pid = db.create_project("P", "#5E5CE6", None).id
    db.add_project_task(pid, "pt")
    db.add_installment("loan", 50000, 6, today.isoformat(), 10)
    db.add_important_date("evt", today.isoformat(), "سایر", "", "none", 0)
    timer = TimerService()

    screens = [
        "home", "finance", "analytics", "settings", "recurring",
        "projects", "project_detail", "installments", "important_dates",
    ]
    for screen in screens:
        state = build_state(
            db=db,
            timer=timer,
            screen=screen,
            current_date=today,
            expanded_tasks=set(),
            analytics_period=7,
            current_project_id=pid if screen == "project_detail" else None,
            finance_year=today.year,
            finance_month=today.month,
        )
        assert state["screen"] == screen


def test_web_bundle_includes_app_js():
    from dailyplanner.ui.shell import build_web_bundle

    bundle = build_web_bundle()
    assert "index.html" in bundle
    assert "app.css" in bundle
    assert "app.js" in bundle
    assert "renderApp" in bundle["app.js"]
    assert "function action(" in bundle["app.js"]


def test_frontend_action_handlers_exist():
    """Every JS action() cmd must have a Python _on_* handler."""
    import re
    from pathlib import Path

    js = (Path(__file__).parents[1] / "src/dailyplanner/ui/static/app.js").read_text(
        encoding="utf-8"
    )
    py = (Path(__file__).parents[1] / "src/dailyplanner/webview_handler.py").read_text(
        encoding="utf-8"
    )
    cmds = set(re.findall(r"action\(\\'([a-z_]+)\\'", js))
    cmds.update(re.findall(r"action\('([a-z_]+)'", js))
    cmds.update(re.findall(r"cmd:\s*'([^']+)'", js))
    handlers = set(re.findall(r"async def _on_([a-z_]+)", py))
    missing = sorted(cmds - handlers)
    assert not missing, f"Missing handlers: {missing}"


def test_app_js_syntax():
    import subprocess
    from pathlib import Path

    app_js = Path(__file__).parents[1] / "src/dailyplanner/ui/static/app.js"
    subprocess.run(["node", "--check", str(app_js)], check=True)


def test_duration_hms_validator_allows_long_hours():
    from pathlib import Path

    js = (Path(__file__).parents[1] / "src/dailyplanner/ui/static/app.js").read_text(
        encoding="utf-8"
    )
    assert "+m[1] <= 99" in js, "duration validator must allow 99-hour estimates"
    assert ".replace(/\\n/g, '\\\\n')" in js, "escJs must escape newlines in onclick strings"


def test_time_picker_logic():
    import subprocess
    from pathlib import Path

    script = Path(__file__).parent / "time_picker_test.js"
    subprocess.run(["node", str(script)], check=True, cwd=str(Path(__file__).parents[1]))


def test_parse_hms_and_hm():
    from dailyplanner.webview_handler import _parse_hm, _parse_hms

    assert _parse_hms("1:30:45") == 5445
    assert _parse_hms("25:00:00") == 90000
    assert _parse_hm("22:30") == 22 * 60 + 30
    assert _parse_hm("23:59") == 23 * 60 + 59
    assert _parse_hms("not-a-time") is None
    assert _parse_hm("") is None


def test_frontend_render_smoke(db, tmp_path):
    """renderApp must not throw for any screen state."""
    import datetime
    import json
    import subprocess
    from pathlib import Path

    today = datetime.date.today()
    db.add_task(today, "Task <test>")
    db.add_finance_entry(today, "expense", "x", 1000, "عمومی")
    pid = db.create_project("P", "#5E5CE6", None).id
    db.add_project_task(pid, "pt")
    db.add_installment("loan", 50000, 6, today.isoformat(), 10)
    db.add_important_date("evt", today.isoformat(), "سایر", "", "none", 0)
    timer = TimerService()

    states = {}
    for screen in (
        "home", "finance", "analytics", "settings", "recurring",
        "projects", "project_detail", "installments", "important_dates",
    ):
        states[screen] = build_state(
            db=db,
            timer=timer,
            screen=screen,
            current_date=today,
            expanded_tasks=set(),
            analytics_period=7,
            current_project_id=pid if screen == "project_detail" else None,
            finance_year=today.year,
            finance_month=today.month,
            show_calendar=True,
            calendar_year=1404,
            calendar_month=4,
        )

    states_file = tmp_path / "states.json"
    states_file.write_text(json.dumps(states, ensure_ascii=False), encoding="utf-8")
    smoke = Path(__file__).parent / "frontend_smoke.js"
    subprocess.run(["node", str(smoke), str(states_file)], check=True, cwd=str(Path(__file__).parents[1]))


def test_validate_backup_rejects_bad_important_dates():
    db = Database(":memory:")
    data = db.export_json()
    data["important_dates"] = "not a list"
    ok, err = db.validate_backup(data)
    assert not ok
    assert "تاریخ" in err


def test_edit_installment_rejects_total_below_paid(db):
    import asyncio
    from dailyplanner.webview_handler import WebViewHandler

    class _App:
        pass

    d = datetime.date.today()
    inst = db.add_installment("loan", 1000, 6, d.isoformat(), 5)
    for _ in range(3):
        db.pay_installment(inst.id)

    app = _App()
    app.db = db
    app.main_window = type("W", (), {"dialog": lambda *a, **k: True})()
    handler = WebViewHandler(app)
    handler._shell_loaded = True

    async def _noop_push(self):
        pass

    handler.push_state = _noop_push.__get__(handler, WebViewHandler)

    async def run():
        await handler._on_edit_installment({
            "id": str(inst.id),
            "title": "loan",
            "amount": "1000",
            "total_count": "2",
            "due_day": "5",
            "start_date": d.isoformat(),
        })

    asyncio.run(run())
    updated = db.get_installment_by_id(inst.id)
    assert updated.total_count == 6
    assert updated.paid_count == 3


def test_open_project_missing_redirects(db):
    import asyncio
    from dailyplanner.webview_handler import WebViewHandler

    class _App:
        pass

    app = _App()
    app.db = db
    app.main_window = type("W", (), {"dialog": lambda *a, **k: True})()
    handler = WebViewHandler(app)
    handler.current_screen = "projects"
    handler._shell_loaded = True

    async def _noop_push(self):
        pass

    handler.push_state = _noop_push.__get__(handler, WebViewHandler)

    async def run():
        await handler._on_open_project({"id": "99999"})

    asyncio.run(run())
    assert handler.current_screen == "projects"
    assert handler.current_project_id is None
