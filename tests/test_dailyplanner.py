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
from dailyplanner.utils.jalali import current_jalali_ym


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

    entries = db.get_investment_entries_between(d.replace(day=1), d)
    assert len(entries) == 1
    assert entries[0].title == "stocks"
    assert db.get_total_investment_until(d) == 200000


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
    assert "tracking_sessions" in data
    assert "tracking_intervals" in data


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
    fin_jy, fin_jm = current_jalali_ym(today)

    screens = [
        "home", "finance", "analytics", "settings", "recurring", "tracking",
        "projects", "project_detail", "installments", "investments", "important_dates",
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
            finance_year=fin_jy,
            finance_month=fin_jm,
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


def test_bundle_fingerprint_changes_with_ui():
    from dailyplanner.utils.platform import bundle_fingerprint

    base = {"index.html": "<html></html>", "app.js": "v1", "app.css": "c1"}
    changed = dict(base)
    changed["app.js"] = "v2"
    fp1 = bundle_fingerprint(base)
    fp2 = bundle_fingerprint(changed)
    assert fp1 != fp2
    assert len(fp1) == 12
    assert bundle_fingerprint(base) == fp1


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
    fin_jy, fin_jm = current_jalali_ym(today)

    states = {}
    for screen in (
        "home", "finance", "analytics", "settings", "recurring", "tracking",
        "projects", "project_detail", "installments", "investments", "important_dates",
    ):
        states[screen] = build_state(
            db=db,
            timer=timer,
            screen=screen,
            current_date=today,
            expanded_tasks=set(),
            analytics_period=7,
            current_project_id=pid if screen == "project_detail" else None,
            finance_year=fin_jy,
            finance_month=fin_jm,
            show_calendar=True,
            calendar_year=1404,
            calendar_month=4,
        )

    states_file = tmp_path / "states.json"
    states_file.write_text(json.dumps(states, ensure_ascii=False), encoding="utf-8")
    smoke = Path(__file__).parent / "frontend_smoke.js"
    subprocess.run(["node", str(smoke), str(states_file)], check=True, cwd=str(Path(__file__).parents[1]))


def test_frontend_audit_renders():
    import subprocess
    from pathlib import Path

    audit = Path(__file__).parent / "audit_renders.js"
    subprocess.run(["node", str(audit)], check=True, cwd=str(Path(__file__).parents[1]))


def test_finance_entry_uses_viewed_month(db):
    import asyncio
    from dailyplanner.utils.jalali import current_jalali_ym, jalali_month_bounds, prev_jalali_month
    from dailyplanner.webview_handler import WebViewHandler

    today = datetime.date.today()
    cur_jy, cur_jm = current_jalali_ym(today)
    fy, fm = prev_jalali_month(cur_jy, cur_jm)
    month_start, month_end = jalali_month_bounds(fy, fm)

    class _App:
        pass

    app = _App()
    app.db = db
    app.main_window = type("W", (), {"dialog": lambda *a, **k: True})()
    handler = WebViewHandler(app)
    handler._shell_loaded = True
    handler.current_screen = "finance"
    handler.finance_year = fy
    handler.finance_month = fm

    async def _noop_push(self):
        pass

    handler.push_state = _noop_push.__get__(handler, WebViewHandler)

    async def run():
        await handler._on_add_finance({
            "type": "expense",
            "title": "test",
            "amount": "1000",
            "category": "عمومی",
        })

    asyncio.run(run())

    entries = db.get_finance_entries_between(month_start, month_end)
    assert len(entries) == 1
    assert month_start.isoformat() <= entries[0].date <= month_end.isoformat()


def test_investment_entry_respects_month_filter(db):
    import asyncio
    from dailyplanner.utils.jalali import current_jalali_ym, jalali_month_bounds, prev_jalali_month
    from dailyplanner.webview_handler import WebViewHandler

    today = datetime.date.today()
    cur_jy, cur_jm = current_jalali_ym(today)
    fy, fm = prev_jalali_month(cur_jy, cur_jm)
    month_start, month_end = jalali_month_bounds(fy, fm)

    class _App:
        pass

    app = _App()
    app.db = db
    app.main_window = type("W", (), {"dialog": lambda *a, **k: True})()
    handler = WebViewHandler(app)
    handler._shell_loaded = True
    handler.current_screen = "investments"
    handler.invest_filter_mode = "month"
    handler.invest_filter_year = fy
    handler.invest_filter_month = fm

    async def _noop_push(self):
        pass

    handler.push_state = _noop_push.__get__(handler, WebViewHandler)

    async def run():
        await handler._on_add_finance({
            "type": "investment",
            "title": "gold",
            "amount": "500000",
            "invest_risk": "کم ریسک",
            "invest_market": "فیزیکی",
            "invest_asset": "طلا",
        })

    asyncio.run(run())

    entries = db.get_investment_entries_between(month_start, month_end)
    assert len(entries) == 1
    assert entries[0].date == month_end.isoformat()
    assert entries[0].entry_type == "investment"
    from dailyplanner.investments import decode_investment_category
    meta = decode_investment_category(entries[0].category)
    assert meta["asset"] == "طلا"
    assert meta["market"] == "فیزیکی"


def test_investment_entry_uses_explicit_date(db):
    import asyncio
    from dailyplanner.webview_handler import WebViewHandler

    today = datetime.date.today()

    class _App:
        pass

    app = _App()
    app.db = db
    app.main_window = type("W", (), {"dialog": lambda *a, **k: True})()
    handler = WebViewHandler(app)
    handler._shell_loaded = True
    handler.current_screen = "investments"

    async def _noop_push(self):
        pass

    handler.push_state = _noop_push.__get__(handler, WebViewHandler)

    async def run():
        await handler._on_add_finance({
            "type": "investment",
            "title": "gold",
            "amount": "500000",
            "date": today.isoformat(),
            "invest_risk": "کم ریسک",
            "invest_market": "فیزیکی",
            "invest_asset": "طلا",
        })

    asyncio.run(run())

    today_entries = db.get_investment_entries_between(today, today)
    assert len(today_entries) == 1
    assert today_entries[0].date == today.isoformat()


def test_investments_state_past_month_snapshot(db):
    from dailyplanner.ui.state import build_state
    from dailyplanner.services.timer import TimerService
    from dailyplanner.utils.jalali import current_jalali_ym, jalali_month_bounds, prev_jalali_month

    today = datetime.date.today()
    cur_jy, cur_jm = current_jalali_ym(today)
    fy, fm = prev_jalali_month(cur_jy, cur_jm)
    month_start, month_end = jalali_month_bounds(fy, fm)

    db.add_finance_entry(month_start, "income", "salary", 1000000, "حقوق")
    db.add_finance_entry(month_end, "investment", "gold", 200000, "طلا")
    db.add_finance_entry(today, "investment", "stocks", 300000, "سهام")

    all_state = build_state(
        db=db,
        timer=TimerService(),
        screen="investments",
        current_date=today,
        expanded_tasks=set(),
        analytics_period=7,
    )
    assert all_state["investments"]["totals"]["portfolio_total"] == 500000
    assert all_state["investments"]["totals"]["balance"] == 500000
    assert len(all_state["investments"]["entries"]) == 2

    month_state = build_state(
        db=db,
        timer=TimerService(),
        screen="investments",
        current_date=today,
        expanded_tasks=set(),
        analytics_period=7,
        invest_filter_mode="month",
        invest_filter_year=fy,
        invest_filter_month=fm,
    )
    assert month_state["investments"]["totals"]["portfolio_total"] == 500000
    assert month_state["investments"]["totals"]["balance"] == 500000
    assert len(month_state["investments"]["entries"]) == 1


def test_investment_taxonomy_encode_decode():
    from dailyplanner.investments import (
        decode_investment_category,
        encode_investment_category,
        get_investment_taxonomy,
        investment_group_key,
        investment_meta_dict,
        is_valid_risk_market,
        markets_for_risk,
    )

    raw = encode_investment_category("کم ریسک", "صندوق", "عیار")
    meta = decode_investment_category(raw)
    assert meta == {"risk": "کم ریسک", "market": "صندوق", "asset": "عیار"}
    assert investment_group_key(raw) == "عیار"

    legacy = decode_investment_category("سهام")
    assert legacy["market"] == "بورس"
    assert legacy["asset"] == "سهام عمومی"

    display = investment_meta_dict(meta)
    assert "عیار" in display["display"]
    assert display["asset_emoji"] == "✨"

    tax = get_investment_taxonomy()
    assert len(tax["risks"]) == 4
    assert len(tax["markets"]) == 9
    assert tax["asset_count"] >= 80
    assert "market_hints" in tax
    assert "units" in tax
    assert "رمزارز" in tax["assets"]
    assert any(x["label"].startswith("BTC/USDT") for x in tax["assets"]["رمزارز"])
    assert tax["units"].get("فیزیکی|طلا") == "گرم"

    low_markets = [m["value"] for m in markets_for_risk("کم ریسک")]
    assert "فیزیکی" in low_markets
    assert "صندوق" in low_markets
    assert "رمزارز" not in low_markets
    high_markets = [m["value"] for m in tax["markets_by_risk"]["پر ریسک"]]
    assert high_markets == ["بورس", "رمزارز"]
    assert is_valid_risk_market("کم ریسک", "صندوق")
    assert not is_valid_risk_market("کم ریسک", "رمزارز")

    from dailyplanner.investments import asset_unit, find_asset
    assert asset_unit("بورس", "فملی") == "سهم"
    assert find_asset("بورس", "فملی")["label"].startswith("فملی")


def test_investment_sell_restores_balance(db):
    d = datetime.date.today()
    db.add_finance_entry(d, "income", "salary", 1000000, "حقوق")
    db.add_finance_entry(
        d, "investment", "gold", 300000, '{"risk":"کم ریسک","market":"فیزیکی","asset":"طلا"}',
        investment_direction="buy",
    )
    assert db.get_finance_balance_until(d) == 700000
    assert db.get_total_investment_until(d) == 300000

    db.add_finance_entry(
        d, "investment", "gold sell", 100000, '{"risk":"کم ریسک","market":"فیزیکی","asset":"طلا"}',
        investment_direction="sell",
    )
    assert db.get_finance_balance_until(d) == 800000
    assert db.get_total_investment_until(d) == 200000


def test_investment_quantity_unit_price(db):
    d = datetime.date.today()
    entry = db.add_finance_entry(
        d, "investment", "BTC", 3000000, '{"risk":"پر ریسک","market":"رمزارز","asset":"BTC/USDT"}',
        quantity=2.0,
        unit_price=1500000,
    )
    assert entry.quantity == 2.0
    assert entry.unit_price == 1500000
    assert entry.amount == 3000000


def test_investment_current_price_and_pnl(db):
    from dailyplanner.investments import investment_pnl_percent

    d = datetime.date.today()
    entry = db.add_finance_entry(
        d, "investment", "gold", 2000000, '{"risk":"کم ریسک","market":"فیزیکی","asset":"طلا"}',
        quantity=1.0,
        unit_price=2000000,
        current_unit_price=2400000,
    )
    assert entry.current_unit_price == 2400000
    assert investment_pnl_percent(entry.unit_price, entry.current_unit_price) == 20.0

    db.update_finance_entry(
        entry.id,
        entry.title,
        entry.amount,
        entry.entry_type,
        entry.category,
        quantity=1.0,
        unit_price=2000000,
        current_unit_price=1800000,
    )
    updated = db.get_finance_entry_by_id(entry.id)
    assert updated.current_unit_price == 1800000
    assert investment_pnl_percent(updated.unit_price, updated.current_unit_price) == -10.0


def test_investment_goal_and_custom_asset(db):
    from dailyplanner.investments import merge_custom_assets, get_investment_taxonomy

    db.set_investment_goal(1404, 1, 5000000)
    assert db.get_investment_goal(1404, 1) == 5000000

    assert db.add_investment_custom_asset("بورس", "خودم", "خودم", "🏭")
    assert not db.add_investment_custom_asset("بورس", "خودم", "خودم")
    custom = db.get_investment_custom_assets()
    assert custom[0]["value"] == "خودم"

    tax = merge_custom_assets(get_investment_taxonomy(), custom)
    assert any(a["value"] == "خودم" for a in tax["assets"]["بورس"])


def test_migrate_legacy_investment_goals_schema(db):
    db.conn.executescript(
        """
        DROP TABLE IF EXISTS investment_goals;
        CREATE TABLE investment_goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            target_amount INTEGER NOT NULL,
            target_date TEXT,
            notes TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL
        );
        """
    )
    db.conn.commit()
    db._migrate_schema()
    cols = {
        row[1] for row in db.conn.execute("PRAGMA table_info(investment_goals)")
    }
    assert cols == {"month_key", "monthly_limit"}
    db.set_investment_goal(1404, 3, 250000)
    assert db.get_investment_goal(1404, 3) == 250000


def test_investment_portfolio_breakdown(db):
    from dailyplanner.investments import encode_investment_category, portfolio_breakdown

    d = datetime.date.today()
    db.add_finance_entry(
        d, "investment", "gold", 200000,
        encode_investment_category("کم ریسک", "فیزیکی", "طلا"),
    )
    db.add_finance_entry(
        d, "investment", "fund", 300000,
        encode_investment_category("کم ریسک", "صندوق", "عیار"),
    )
    entries = db.get_investment_entries_until(d)
    breakdown = portfolio_breakdown(entries)
    assert breakdown["by_asset"]["طلا"] == 200000
    assert breakdown["by_asset"]["عیار"] == 300000
    assert breakdown["by_risk"]["کم ریسک"] == 500000


def test_investment_positions_and_sell_validation(db):
    from dailyplanner.investments import (
        compute_positions,
        encode_investment_category,
        merge_asset_prices,
        validate_investment_sell,
    )

    d = datetime.date.today()
    cat = encode_investment_category("کم ریسک", "فیزیکی", "طلا")
    db.add_finance_entry(
        d, "investment", "gold", 300000, cat,
        quantity=2.0, unit_price=150000, current_unit_price=180000,
    )

    entries = db.get_investment_entries_until(d)
    prices = merge_asset_prices(db.get_investment_asset_prices(), entries)
    positions = compute_positions(entries, prices)
    assert len(positions) == 1
    assert positions[0]["quantity"] == 2.0
    assert positions[0]["cost_basis"] == 300000
    assert positions[0]["estimated_value"] == 360000
    assert positions[0]["unrealized_pnl"] == 60000

    assert validate_investment_sell(cat, 400000, None, entries)
    assert validate_investment_sell(cat, 100000, 3.0, entries)

    db.add_finance_entry(
        d, "investment", "sell", 100000, cat,
        investment_direction="sell", quantity=1.0,
    )
    entries2 = db.get_investment_entries_until(d)
    positions2 = compute_positions(entries2, prices)
    assert positions2[0]["quantity"] == 1.0
    assert positions2[0]["cost_basis"] == 150000


def test_investment_asset_price_setting(db):
    assert db.set_investment_asset_price("فیزیکی", "طلا", 2000000)
    prices = db.get_investment_asset_prices()
    assert prices["فیزیکی|طلا"] == 2000000
    assert db.delete_investment_asset_price("فیزیکی", "طلا")
    assert "فیزیکی|طلا" not in db.get_investment_asset_prices()


def test_investment_edit_date_persisted(db):
    from dailyplanner.investments import encode_investment_category
    from dailyplanner.models import date_to_str

    old_date = datetime.date.today() - datetime.timedelta(days=10)
    new_date = datetime.date.today() - datetime.timedelta(days=3)
    cat = encode_investment_category("کم ریسک", "فیزیکی", "طلا")
    entry = db.add_finance_entry(old_date, "investment", "gold", 100000, cat)
    db.update_finance_entry(
        entry.id, "gold", 100000, "investment", cat, entry_date=new_date
    )
    updated = db.get_finance_entry_by_id(entry.id)
    assert updated.date == date_to_str(new_date)


def test_investment_quantity_inferred_from_amount_and_unit_price(db):
    from dailyplanner.investments import (
        compute_positions,
        encode_investment_category,
        merge_asset_prices,
    )

    d = datetime.date.today()
    cat = encode_investment_category("کم ریسک", "فیزیکی", "طلا")
    db.add_finance_entry(
        d, "investment", "gold", 300000, cat, unit_price=150000,
    )
    db.set_investment_asset_price("فیزیکی", "طلا", 180000)
    entries = db.get_investment_entries_until(d)
    prices = merge_asset_prices(db.get_investment_asset_prices(), entries)
    positions = compute_positions(entries, prices)
    assert len(positions) == 1
    assert positions[0]["quantity"] == 2.0
    assert positions[0]["estimated_value"] == 360000
    assert positions[0]["has_market_price"]


def test_allocation_comparison_uses_market_asset_key(db):
    from dailyplanner.investments import (
        compute_allocation_comparison,
        compute_positions,
        encode_investment_category,
        merge_asset_prices,
    )

    d = datetime.date.today()
    cat1 = encode_investment_category("کم ریسک", "فیزیکی", "طلا")
    cat2 = encode_investment_category("کم ریسک", "صندوق", "عیار")
    db.add_finance_entry(
        d, "investment", "gold", 200000, cat1,
        quantity=1.0, unit_price=200000, current_unit_price=200000,
    )
    db.add_finance_entry(
        d, "investment", "fund", 300000, cat2,
        quantity=1.0, unit_price=300000, current_unit_price=300000,
    )
    entries = db.get_investment_entries_until(d)
    prices = merge_asset_prices(db.get_investment_asset_prices(), entries)
    positions = compute_positions(entries, prices)
    targets = {"فیزیکی|طلا": 40, "صندوق|عیار": 60}
    items = compute_allocation_comparison(positions, targets)
    by_key = {i["key"]: i for i in items}
    assert by_key["فیزیکی|طلا"]["actual_value"] == 200000
    assert by_key["صندوق|عیار"]["actual_value"] == 300000


def test_legacy_and_json_categories_merge_in_positions(db):
    from dailyplanner.investments import (
        compute_positions,
        encode_investment_category,
        validate_investment_sell,
    )

    d = datetime.date.today()
    json_cat = encode_investment_category("کم ریسک", "فیزیکی", "طلا")
    db.add_finance_entry(d, "investment", "legacy", 100000, "طلا")
    db.add_finance_entry(
        d, "investment", "json", 200000, json_cat,
        quantity=1.0, unit_price=200000,
    )
    entries = db.get_investment_entries_until(d)
    positions = compute_positions(entries)
    assert len(positions) == 1
    assert positions[0]["cost_basis"] == 300000
    assert validate_investment_sell(json_cat, 50000, None, entries) is None


def test_amount_only_sell_reduces_quantity(db):
    from dailyplanner.investments import compute_positions, encode_investment_category

    d = datetime.date.today()
    cat = encode_investment_category("کم ریسک", "فیزیکی", "طلا")
    db.add_finance_entry(
        d, "investment", "buy", 300000, cat,
        quantity=2.0, unit_price=150000,
    )
    db.add_finance_entry(
        d, "investment", "sell", 150000, cat,
        investment_direction="sell",
    )
    db.set_investment_asset_price("فیزیکی", "طلا", 180000)
    entries = db.get_investment_entries_until(d)
    positions = compute_positions(entries, db.get_investment_asset_prices())
    assert len(positions) == 1
    assert positions[0]["quantity"] == 1.0
    assert positions[0]["cost_basis"] == 150000
    assert positions[0]["estimated_value"] == 180000


def test_buy_without_current_price_keeps_stored_price(db):
    from dailyplanner.webview_handler import _sync_investment_asset_price

    db.set_investment_asset_price("فیزیکی", "طلا", 2500000)
    _sync_investment_asset_price(db, "فیزیکی", "طلا", None)
    assert db.get_investment_asset_prices()["فیزیکی|طلا"] == 2500000


def test_edit_buy_to_sell_validation_credits_excluded_entry(db):
    from dailyplanner.investments import encode_investment_category, validate_investment_sell

    d = datetime.date.today()
    cat = encode_investment_category("کم ریسک", "فیزیکی", "طلا")
    entry = db.add_finance_entry(
        d, "investment", "gold", 200000, cat,
        quantity=1.0, unit_price=200000,
    )
    entries = db.get_investment_entries_until(d)
    assert validate_investment_sell(cat, 100000, None, entries, exclude_id=entry.id) is None


def test_amount_and_quantity_without_unit_price(db):
    from dailyplanner.webview_handler import _resolve_investment_amount

    amount, qty, unit_price, err = _resolve_investment_amount({
        "amount": "300000",
        "quantity": "2",
    })
    assert err == ""
    assert amount == 300000
    assert qty == 2.0
    assert unit_price == 150000


def test_rebalance_sell_capped_at_cost_basis(db):
    from dailyplanner.investments import (
        compute_positions,
        compute_rebalance_suggestions,
        encode_investment_category,
        merge_asset_prices,
    )

    d = datetime.date.today()
    cat = encode_investment_category("کم ریسک", "فیزیکی", "طلا")
    db.add_finance_entry(
        d, "investment", "gold", 200000, cat,
        quantity=1.0, unit_price=200000, current_unit_price=200000,
    )
    db.set_investment_asset_price("فیزیکی", "طلا", 400000)
    entries = db.get_investment_entries_until(d)
    prices = merge_asset_prices(db.get_investment_asset_prices(), entries)
    positions = compute_positions(entries, prices)
    targets = {"فیزیکی|طلا": 10, "صندوق|عیار": 90}
    rebalance = compute_rebalance_suggestions(positions, targets)
    gold_sell = next(
        (i for i in rebalance["items"] if i.get("asset") == "طلا" and i.get("action") == "sell"),
        None,
    )
    assert gold_sell is not None
    assert gold_sell["amount"] <= 200000


def test_edit_sell_validation_credits_excluded_sell(db):
    from dailyplanner.investments import encode_investment_category, validate_investment_sell

    d = datetime.date.today()
    cat = encode_investment_category("کم ریسک", "فیزیکی", "طلا")
    db.add_finance_entry(
        d, "investment", "buy", 300000, cat,
        quantity=3.0, unit_price=100000,
    )
    sell1 = db.add_finance_entry(
        d, "investment", "sell1", 100000, cat,
        investment_direction="sell", quantity=1.0,
    )
    db.add_finance_entry(
        d, "investment", "sell2", 100000, cat,
        investment_direction="sell", quantity=1.0,
    )
    entries = db.get_investment_entries_until(d)
    assert validate_investment_sell(cat, 250000, 2.5, entries, exclude_id=sell1.id) is None


def test_edit_buy_cannot_go_below_sells(db):
    from dailyplanner.investments import encode_investment_category, validate_investment_buy_edit

    d = datetime.date.today()
    cat = encode_investment_category("کم ریسک", "فیزیکی", "طلا")
    buy = db.add_finance_entry(
        d, "investment", "buy", 300000, cat,
        quantity=3.0, unit_price=100000,
    )
    db.add_finance_entry(
        d, "investment", "sell", 150000, cat,
        investment_direction="sell", quantity=1.5,
    )
    entries = db.get_investment_entries_until(d)
    err = validate_investment_buy_edit(
        cat, 100000, 1.0, entries, exclude_id=buy.id, old_category=cat
    )
    assert err is not None
    assert validate_investment_buy_edit(
        cat, 200000, 2.0, entries, exclude_id=buy.id, old_category=cat
    ) is None


def test_custom_asset_rejects_builtin_duplicate(db):
    assert not db.add_investment_custom_asset("فیزیکی", "طلا", "طلا")


def test_investments_state_has_positions(db):
    from dailyplanner.investments import encode_investment_category
    from dailyplanner.ui.state import build_state
    from dailyplanner.services.timer import TimerService

    d = datetime.date.today()
    cat = encode_investment_category("کم ریسک", "فیزیکی", "طلا")
    db.add_finance_entry(
        d, "investment", "gold", 200000, cat,
        quantity=1.0, unit_price=200000, current_unit_price=240000,
    )
    db.set_investment_asset_price("فیزیکی", "طلا", 240000)

    state = build_state(
        db=db,
        timer=TimerService(),
        screen="investments",
        current_date=d,
        expanded_tasks=set(),
        analytics_period=7,
    )
    inv = state["investments"]
    assert len(inv["positions"]) == 1
    assert inv["totals"]["net_invested"] == 200000
    assert inv["totals"]["estimated_value"] == 240000
    assert inv["totals"]["has_market_values"] is True


def test_investment_goal_uses_buys_only(db):
    from dailyplanner.investments import encode_investment_category
    from dailyplanner.ui.state import build_state
    from dailyplanner.services.timer import TimerService
    from dailyplanner.utils.jalali import current_jalali_ym, jalali_month_bounds

    today = datetime.date.today()
    cur_jy, cur_jm = current_jalali_ym(today)
    month_start, _ = jalali_month_bounds(cur_jy, cur_jm)
    cat = encode_investment_category("کم ریسک", "فیزیکی", "طلا")

    db.add_finance_entry(month_start, "investment", "buy", 300000, cat)
    db.add_finance_entry(
        month_start, "investment", "sell", 100000, cat, investment_direction="sell",
    )
    db.set_investment_goal(cur_jy, cur_jm, 500000)

    state = build_state(
        db=db,
        timer=TimerService(),
        screen="investments",
        current_date=today,
        expanded_tasks=set(),
        analytics_period=7,
        invest_filter_mode="month",
        invest_filter_year=cur_jy,
        invest_filter_month=cur_jm,
    )
    inv = state["investments"]
    assert inv["totals"]["period_buys"] == 300000
    assert inv["goal_pct"] == 60
    assert not inv["over_goal"]


def test_investments_state_includes_goal_and_chart(db):
    from dailyplanner.ui.state import build_state
    from dailyplanner.services.timer import TimerService
    from dailyplanner.utils.jalali import current_jalali_ym, jalali_month_bounds

    today = datetime.date.today()
    cur_jy, cur_jm = current_jalali_ym(today)
    month_start, month_end = jalali_month_bounds(cur_jy, cur_jm)

    db.add_finance_entry(month_start, "investment", "gold", 100000, "طلا")
    db.set_investment_goal(cur_jy, cur_jm, 500000)

    state = build_state(
        db=db,
        timer=TimerService(),
        screen="investments",
        current_date=today,
        expanded_tasks=set(),
        analytics_period=7,
        invest_filter_mode="month",
        invest_filter_year=cur_jy,
        invest_filter_month=cur_jm,
        finance_year=cur_jy,
        finance_month=cur_jm,
    )
    inv = state["investments"]
    assert inv["goal"] == 500000
    assert inv["chart"]["has_data"] is True
    assert len(inv["all_entries"]) == 1
    assert "portfolio_by_category" in inv
    assert "portfolio_by_risk" in inv


def test_investments_all_mode_includes_all_entries(db):
    from dailyplanner.ui.state import build_state
    from dailyplanner.services.timer import TimerService
    from dailyplanner.utils.jalali import current_jalali_ym, jalali_month_bounds

    today = datetime.date.today()
    cur_jy, cur_jm = current_jalali_ym(today)
    month_start, _ = jalali_month_bounds(cur_jy, cur_jm)

    db.add_finance_entry(month_start, "investment", "gold", 100000, "طلا")
    db.add_finance_entry(today, "investment", "stocks", 200000, "سهام")

    state = build_state(
        db=db,
        timer=TimerService(),
        screen="investments",
        current_date=today,
        expanded_tasks=set(),
        analytics_period=7,
        invest_filter_mode="all",
        finance_year=cur_jy,
        finance_month=cur_jm,
    )
    inv = state["investments"]
    assert len(inv["entries"]) == 2
    assert len(inv["all_entries"]) == 2


def test_investment_allocation_targets(db):
    from dailyplanner.investments import (
        compute_allocation_comparison,
        encode_investment_category,
        compute_positions,
        merge_asset_prices,
    )
    from dailyplanner.ui.state import build_state
    from dailyplanner.services.timer import TimerService

    d = datetime.date.today()
    cat_gold = encode_investment_category("کم ریسک", "فیزیکی", "طلا")
    cat_fund = encode_investment_category("کم ریسک", "صندوق", "عیار")
    db.add_finance_entry(
        d, "investment", "gold", 300000, cat_gold,
        quantity=1.0, unit_price=300000, current_unit_price=300000,
    )
    db.add_finance_entry(
        d, "investment", "fund", 700000, cat_fund,
        quantity=1.0, unit_price=700000, current_unit_price=700000,
    )
    db.set_investment_asset_price("فیزیکی", "طلا", 300000)
    db.set_investment_asset_price("صندوق", "عیار", 700000)
    db.set_investment_allocation_target("فیزیکی", "طلا", 30)
    db.set_investment_allocation_target("صندوق", "عیار", 70)

    entries = db.get_investment_entries_until(d)
    prices = merge_asset_prices(db.get_investment_asset_prices(), entries)
    positions = compute_positions(entries, prices)
    comparison = compute_allocation_comparison(positions, db.get_investment_allocation_targets())
    gold = next(c for c in comparison if c["asset"] == "طلا")
    assert gold["target_pct"] == 30
    assert gold["actual_pct"] == 30.0

    state = build_state(
        db=db, timer=TimerService(), screen="investments",
        current_date=d, expanded_tasks=set(), analytics_period=7,
    )
    inv = state["investments"]
    assert inv["allocation_targets_total"] == 100
    assert any(a["asset"] == "طلا" and a["target_pct"] == 30 for a in inv["allocation"])


def test_investment_rebalance_suggestions(db):
    from dailyplanner.investments import (
        compute_rebalance_suggestions,
        encode_investment_category,
        compute_positions,
        merge_asset_prices,
    )
    from dailyplanner.ui.state import build_state
    from dailyplanner.services.timer import TimerService

    d = datetime.date.today()
    cat_gold = encode_investment_category("کم ریسک", "فیزیکی", "طلا")
    cat_fund = encode_investment_category("کم ریسک", "صندوق", "عیار")
    db.add_finance_entry(
        d, "investment", "gold", 700000, cat_gold,
        quantity=1.0, unit_price=700000, current_unit_price=700000,
    )
    db.add_finance_entry(
        d, "investment", "fund", 300000, cat_fund,
        quantity=1.0, unit_price=300000, current_unit_price=300000,
    )
    db.set_investment_asset_price("فیزیکی", "طلا", 700000)
    db.set_investment_asset_price("صندوق", "عیار", 300000)
    db.set_investment_allocation_target("فیزیکی", "طلا", 30)
    db.set_investment_allocation_target("صندوق", "عیار", 70)

    entries = db.get_investment_entries_until(d)
    prices = merge_asset_prices(db.get_investment_asset_prices(), entries)
    positions = compute_positions(entries, prices)
    rebalance = compute_rebalance_suggestions(positions, db.get_investment_allocation_targets())

    assert rebalance["has_suggestions"] is True
    assert rebalance["total_buy"] == 400000
    assert rebalance["total_sell"] == 400000
    assert rebalance["net_cash_needed"] == 0

    gold_item = next(i for i in rebalance["items"] if i["asset"] == "طلا")
    fund_item = next(i for i in rebalance["items"] if i["asset"] == "عیار")
    assert gold_item["action"] == "sell"
    assert gold_item["amount"] == 400000
    assert fund_item["action"] == "buy"
    assert fund_item["amount"] == 400000

    state = build_state(
        db=db, timer=TimerService(), screen="investments",
        current_date=d, expanded_tasks=set(), analytics_period=7,
    )
    inv = state["investments"]
    assert inv["rebalance"]["has_suggestions"] is True
    assert inv["rebalance"]["total_buy_fmt"]


def test_investment_rebalance_balanced_no_suggestions(db):
    from dailyplanner.investments import (
        compute_rebalance_suggestions,
        encode_investment_category,
        compute_positions,
        merge_asset_prices,
    )

    d = datetime.date.today()
    cat_gold = encode_investment_category("کم ریسک", "فیزیکی", "طلا")
    cat_fund = encode_investment_category("کم ریسک", "صندوق", "عیار")
    db.add_finance_entry(
        d, "investment", "gold", 300000, cat_gold,
        quantity=1.0, unit_price=300000, current_unit_price=300000,
    )
    db.add_finance_entry(
        d, "investment", "fund", 700000, cat_fund,
        quantity=1.0, unit_price=700000, current_unit_price=700000,
    )
    db.set_investment_allocation_target("فیزیکی", "طلا", 30)
    db.set_investment_allocation_target("صندوق", "عیار", 70)

    entries = db.get_investment_entries_until(d)
    prices = merge_asset_prices(db.get_investment_asset_prices(), entries)
    positions = compute_positions(entries, prices)
    rebalance = compute_rebalance_suggestions(positions, db.get_investment_allocation_targets())

    assert rebalance["has_suggestions"] is False
    assert all(i["action"] == "hold" for i in rebalance["items"])


def test_investment_custom_asset_edit_delete(db):
    from dailyplanner.investments import is_builtin_asset

    assert db.add_investment_custom_asset("بورس", "نمادمن", "نمادمن", "🏭")
    assert db.update_investment_custom_asset("بورس", "نمادمن", label="نماد سفارشی", emoji="🔩")
    custom = db.get_investment_custom_assets()
    assert custom[0]["label"] == "نماد سفارشی"
    assert custom[0]["emoji"] == "🔩"
    assert is_builtin_asset("بورس", "فولاد") is True
    assert is_builtin_asset("بورس", "نمادمن") is False
    assert db.delete_investment_custom_asset("بورس", "نمادمن")
    assert not db.get_investment_custom_assets()


def test_investment_custom_asset_delete_blocked_with_entries(db):
    from dailyplanner.investments import encode_investment_category

    d = datetime.date.today()
    cat = encode_investment_category("ریسک متوسط", "بورس", "نمادمن")
    db.add_investment_custom_asset("بورس", "نمادمن", "نمادمن")
    db.add_finance_entry(d, "investment", "buy", 100000, cat)
    assert db.count_investment_entries_for_asset("بورس", "نمادمن") == 1
    assert not db.delete_investment_custom_asset("بورس", "نمادمن")
    assert db.get_investment_custom_assets()


def test_validate_backup_rejects_bad_important_dates():
    db = Database(":memory:")
    data = db.export_json()
    data["important_dates"] = "not a list"
    ok, err = db.validate_backup(data)
    assert not ok
    assert "تاریخ" in err


def test_validate_backup_accepts_investment_sell():
    db = Database(":memory:")
    data = db.export_json()
    data["finance"] = [{
        "id": 1,
        "date": "2026-06-22",
        "entry_type": "investment",
        "title": "sell gold",
        "amount": 1000,
        "category": "طلا",
        "investment_direction": "sell",
        "quantity": 2,
        "unit_price": 500,
    }]
    ok, err = db.validate_backup(data)
    assert ok, err


def test_pay_installment_creates_finance_expense(db):
    import asyncio
    from dailyplanner.webview_handler import WebViewHandler

    d = datetime.date.today()
    inst = db.add_installment("loan", 50000, 6, d.isoformat(), 10)

    class _App:
        pass

    app = _App()
    app.db = db
    app.main_window = type("W", (), {"dialog": lambda *a, **k: True})()
    handler = WebViewHandler(app)
    handler._shell_loaded = True

    async def _noop_push(self):
        pass

    handler.push_state = _noop_push.__get__(handler, WebViewHandler)

    async def run():
        await handler._on_pay_installment({"id": str(inst.id)})

    asyncio.run(run())

    entries = db.get_finance_entries_for_month(d.year, d.month)
    assert len(entries) == 1
    assert entries[0].amount == 50000
    assert entries[0].entry_type == "expense"
    assert entries[0].category == "اقساط"
    assert "قسط" in entries[0].title
    updated = db.get_installment_by_id(inst.id)
    assert updated.paid_count == 1


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


def test_delete_tracking_interval(db):
    import datetime
    import time

    d = datetime.date.today()
    sid = db.start_tracking_session(d)
    db.switch_tracking(sid)
    intervals = db.get_tracking_intervals(sid)
    assert len(intervals) == 2
    completed_id = intervals[0]["id"]
    db.conn.execute(
        "UPDATE tracking_intervals SET ended_at=?, duration_secs=? WHERE id=?",
        (time.time(), 60, completed_id),
    )
    db.conn.commit()

    assert db.delete_tracking_interval(completed_id)
    remaining = db.get_tracking_intervals(sid)
    assert len(remaining) == 1
    assert remaining[0]["ended_at"] is None

    active_id = remaining[0]["id"]
    assert not db.delete_tracking_interval(active_id)


def test_delete_tracking_session(db):
    import datetime

    d = datetime.date.today()
    sid = db.start_tracking_session(d)
    db.switch_tracking(sid)
    assert db.delete_tracking_session(sid)
    assert db.get_tracking_sessions_for_date(d) == []
    assert db.get_active_tracking_session(d) is None


def test_useful_totals_include_tracking(db):
    import datetime
    import time

    d = datetime.date.today()
    task = db.add_task(d, "task")
    db.set_useful(task.id, True)
    db.add_duration(task.id, 100)

    sid = db.start_tracking_session(d)
    interval = db.get_tracking_intervals(sid)[0]
    now = time.time()
    db.conn.execute(
        "UPDATE tracking_intervals SET ended_at=?, duration_secs=?, is_useful=? WHERE id=?",
        (now, 200, 1, interval["id"]),
    )
    db.conn.commit()

    useful, not_useful = db.get_useful_totals(d)
    assert useful == 300
    assert not_useful == 0


def test_tasks_summary_includes_tracking(db):
    import datetime
    import time

    d = datetime.date.today()
    sid = db.start_tracking_session(d)
    interval = db.get_tracking_intervals(sid)[0]
    now = time.time()
    db.conn.execute(
        "UPDATE tracking_intervals SET ended_at=?, duration_secs=?, is_useful=? WHERE id=?",
        (now, 450, 0, interval["id"]),
    )
    db.conn.commit()

    rows = db.get_tasks_summary_for_range(d, d)
    assert len(rows) == 1
    assert rows[0]["not_useful"] == 450
    assert rows[0]["total"] == 450


def test_day_activity_seconds_includes_unclassified_tracking(db):
    import datetime
    import time

    d = datetime.date.today()
    sid = db.start_tracking_session(d)
    interval = db.get_tracking_intervals(sid)[0]
    now = time.time()
    db.conn.execute(
        "UPDATE tracking_intervals SET ended_at=?, duration_secs=? WHERE id=?",
        (now, 300, interval["id"]),
    )
    db.conn.commit()

    assert db.get_day_activity_seconds(d) == 300
    useful, not_useful = db.get_useful_totals(d)
    assert useful == 0 and not_useful == 0


def test_import_json_clears_tracking(db):
    import datetime

    d = datetime.date.today()
    db.start_tracking_session(d)
    assert db.get_tracking_sessions_for_date(d)

    exported = db.export_json()
    exported.pop("tracking_sessions", None)
    exported.pop("tracking_intervals", None)
    db.import_json(exported)
    assert db.get_tracking_sessions_for_date(d) == []


def test_backup_tracking_roundtrip(db):
    import datetime

    d = datetime.date.today()
    sid = db.start_tracking_session(d)
    db.stop_tracking(sid)
    assert db.get_tracking_sessions_for_date(d)

    exported = db.export_json()
    db.import_json(exported)
    restored = db.get_tracking_sessions_for_date(d)
    assert len(restored) == 1
    assert restored[0]["id"] == sid


def test_pay_installment_past_jalali_month_no_duplicate(db):
    import asyncio
    from dailyplanner.utils.jalali import current_jalali_ym, jalali_month_bounds, prev_jalali_month
    from dailyplanner.webview_handler import WebViewHandler

    today = datetime.date.today()
    cur_jy, cur_jm = current_jalali_ym(today)
    fy, fm = prev_jalali_month(cur_jy, cur_jm)
    month_start, month_end = jalali_month_bounds(fy, fm)
    inst = db.add_installment("loan", 50000, 6, today.isoformat(), 10)

    class _App:
        pass

    app = _App()
    app.db = db
    app.main_window = type("W", (), {"dialog": lambda *a, **k: True})()
    handler = WebViewHandler(app)
    handler._shell_loaded = True
    handler.current_screen = "finance"
    handler.finance_year = fy
    handler.finance_month = fm

    async def _noop_push(self):
        pass

    handler.push_state = _noop_push.__get__(handler, WebViewHandler)

    async def run():
        await handler._on_pay_installment({"id": str(inst.id)})
        await handler._on_pay_installment({"id": str(inst.id)})

    asyncio.run(run())

    updated = db.get_installment_by_id(inst.id)
    assert updated.paid_count == 1
    payments = db.conn.execute(
        "SELECT payment_date FROM installment_payments WHERE installment_id=?",
        (inst.id,),
    ).fetchall()
    assert len(payments) == 1
    assert month_start.isoformat() <= payments[0]["payment_date"] <= month_end.isoformat()
    entries = db.get_finance_entries_between(month_start, month_end)
    assert len(entries) == 1


def test_validate_backup_rejects_paid_over_total():
    db = Database(":memory:")
    data = db.export_json()
    data["installments"] = [{
        "id": 1,
        "title": "loan",
        "amount": 1000,
        "total_count": 2,
        "paid_count": 5,
        "start_date": "2026-06-01",
        "due_day": 1,
        "created_at": "",
    }]
    ok, err = db.validate_backup(data)
    assert not ok
    assert "اقساط" in err


def test_switch_tracking_rejects_ended_session(db):
    import datetime

    d = datetime.date.today()
    sid = db.start_tracking_session(d)
    assert db.stop_tracking(sid)
    assert not db.switch_tracking(sid)


def test_parse_hms_rejects_negative():
    from dailyplanner.webview_handler import _parse_hms

    assert _parse_hms("-1:00:00") is None
    assert _parse_hms("1:-30:00") is None


def test_start_tracking_reuses_active_session(db):
    import datetime

    d = datetime.date.today()
    sid1 = db.start_tracking_session(d)
    sid2 = db.start_tracking_session(d)
    assert sid1 == sid2
    assert len(db.get_tracking_sessions_for_date(d)) == 1


def test_close_stale_tracking_sessions(db):
    import datetime
    import time

    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    now = time.time()
    cur = db.conn.execute(
        "INSERT INTO tracking_sessions (date, started_at, created_at) VALUES (?,?,?)",
        (yesterday.isoformat(), now - 3600, datetime.datetime.now().isoformat()),
    )
    session_id = cur.lastrowid
    db.conn.execute(
        "INSERT INTO tracking_intervals (session_id, started_at) VALUES (?,?)",
        (session_id, now - 3600),
    )
    db.conn.commit()

    db.close_stale_tracking_sessions(datetime.date.today())
    row = db.conn.execute(
        "SELECT ended_at FROM tracking_sessions WHERE id=?", (session_id,)
    ).fetchone()
    assert row["ended_at"] is not None


def test_recurring_instance_sort_order(db):
    import datetime

    d = datetime.date.today()
    db.add_task(d, "manual")
    db.create_recurring("daily habit")
    RecurringService(db).ensure_daily_tasks(d)
    tasks = db.get_tasks_for_date(d)
    assert len(tasks) == 2
    assert tasks[0].title == "manual"
    assert tasks[1].title == "daily habit"
