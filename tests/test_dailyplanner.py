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


def test_str_to_date():
    assert str_to_date("2026-06-22") == datetime.date(2026, 6, 22)
