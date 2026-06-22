"""WebView action handler — SPA state + JS→Python actions."""
import asyncio
import base64
import datetime
import json
from typing import Optional, Set

import toga

from dailyplanner.database import Database
from dailyplanner.models import format_duration, str_to_date
from dailyplanner.services.recurring import RecurringService
from dailyplanner.services.timer import TimerService
from dailyplanner.ui.shell import build_web_bundle
from dailyplanner.ui.state import build_state
from dailyplanner.utils.jalali import gregorian_to_jalali_parts, jalali_to_gregorian
from dailyplanner.utils.platform import set_webview_bundle


class WebViewHandler:
    def __init__(self, app):
        self.app = app
        self.db: Database = app.db
        self.timer_service = TimerService()
        self.recurring_svc = RecurringService(self.db)

        self.current_screen: str = "home"
        self.current_date: datetime.date = datetime.date.today()
        self.expanded_tasks: Set[int] = set()
        self.analytics_period: int = 7
        self.search_query: str = ""
        self.show_calendar: bool = False
        self.calendar_year: Optional[int] = None
        self.calendar_month: Optional[int] = None
        self.finance_month: int = datetime.date.today().month
        self.finance_year: int = datetime.date.today().year
        self._shell_loaded: bool = False
        self._pending_toast: Optional[dict] = None
        self._restore_active_timer()

    # ── timer persistence ─────────────────────────────────────────────────────

    def _restore_active_timer(self):
        active = self.db.get_active_timer()
        if not active:
            return
        task_id, started_at = active
        if not self.db.get_task_by_id(task_id):
            self.db.clear_active_timer()
            return
        self.timer_service.restore(task_id, started_at)

    def _persist_active_timer(self):
        task_id = self.timer_service.active_task_id
        started_at = self.timer_service.start_epoch
        if task_id is None or started_at is None:
            self.db.clear_active_timer()
        else:
            self.db.set_active_timer(task_id, started_at)

    def _stop_timer_and_save(self) -> None:
        task_id, elapsed = self.timer_service.stop()
        if task_id and elapsed > 0:
            self.db.add_duration(task_id, elapsed)
        self.db.clear_active_timer()

    # ── SPA loading ───────────────────────────────────────────────────────────

    def load_shell(self):
        bundle = build_web_bundle()
        set_webview_bundle(self.app.webview, bundle, window=self.app.main_window)
        self._shell_loaded = True

    def _build_state(self) -> dict:
        if self.current_screen == "home":
            self.recurring_svc.ensure_daily_tasks(self.current_date)
        toast = self._pending_toast
        self._pending_toast = None
        return build_state(
            db=self.db,
            timer=self.timer_service,
            screen=self.current_screen,
            current_date=self.current_date,
            expanded_tasks=self.expanded_tasks,
            analytics_period=self.analytics_period,
            search_query=self.search_query,
            show_calendar=self.show_calendar,
            calendar_year=self.calendar_year,
            calendar_month=self.calendar_month,
            finance_year=self.finance_year,
            finance_month=self.finance_month,
            toast=toast,
        )

    async def push_state(self):
        if not self._shell_loaded:
            self.load_shell()
            await asyncio.sleep(0.3)

        for _ in range(30):
            try:
                ready = await self.app.webview.evaluate_javascript("!!window.renderApp")
            except Exception:
                ready = False
            if ready:
                break
            await asyncio.sleep(0.1)

        state = self._build_state()
        payload = json.dumps(state, ensure_ascii=False)
        b64 = base64.b64encode(payload.encode("utf-8")).decode("ascii")
        js = (
            "try{var _b=atob('" + b64 + "');"
            "var _u=new Uint8Array(_b.length);"
            "for(var i=0;i<_b.length;i++)_u[i]=_b.charCodeAt(i);"
            "var _s=new TextDecoder('utf-8').decode(_u);"
            "if(window.renderApp)window.renderApp(JSON.parse(_s));"
            "}catch(e){console.error('renderApp',e);}"
        )
        try:
            await self.app.webview.evaluate_javascript(js)
        except Exception as exc:
            print(f"[push_state] failed: {exc}")

    def push_state_sync(self):
        asyncio.create_task(self.push_state())

    def toast(self, message: str, type: str = ""):
        self._pending_toast = {"message": message, "type": type}

    # ── background loops ──────────────────────────────────────────────────────

    async def poll_loop(self, _app=None, **kwargs):
        while True:
            try:
                raw = await self.app.webview.evaluate_javascript(
                    "var a=window._actions||[];window._actions=[];JSON.stringify(a);"
                )
                if raw and raw not in (None, "null", "[]", '""'):
                    if isinstance(raw, str) and raw.startswith('"'):
                        raw = json.loads(raw)
                    actions = json.loads(raw) if isinstance(raw, str) else raw
                    if isinstance(actions, list):
                        for item in actions:
                            if isinstance(item, dict):
                                await self.handle_action(
                                    item.get("cmd", ""),
                                    item.get("params", {}),
                                )
            except Exception:
                pass
            await asyncio.sleep(0.1)

    async def timer_update_loop(self, _app=None, **kwargs):
        while True:
            task_id = self.timer_service.active_task_id
            if task_id is not None and self.current_screen == "home":
                task = self.db.get_task_by_id(task_id)
                if task:
                    total = task.duration_seconds + self.timer_service.get_elapsed()
                    display = format_duration(total)
                    try:
                        await self.app.webview.evaluate_javascript(
                            f"if(window.updateTimer)updateTimer({task_id},'{display}');"
                        )
                    except Exception:
                        pass
            await asyncio.sleep(1)

    # ── action dispatcher ─────────────────────────────────────────────────────

    async def handle_action(self, cmd: str, params: dict):
        try:
            handler = getattr(self, f"_on_{cmd}", None)
            if handler:
                await handler(params)
        except Exception as e:
            print(f"[action error] {cmd}: {e}")
            self.toast(f"خطا: {cmd}", "error")
            await self.push_state()

    # ── navigation ────────────────────────────────────────────────────────────

    async def _on_navigate(self, p):
        screen = p.get("screen", "home")
        self.current_screen = screen
        await self.push_state()

    async def _on_prev_day(self, p):
        self.current_date -= datetime.timedelta(days=1)
        await self.push_state()

    async def _on_next_day(self, p):
        self.current_date += datetime.timedelta(days=1)
        await self.push_state()

    async def _on_today(self, p):
        self.current_date = datetime.date.today()
        await self.push_state()

    async def _on_pick_date(self, p):
        date_str = p.get("date", "")
        try:
            self.current_date = str_to_date(date_str)
            self.show_calendar = False
            await self.push_state()
        except ValueError:
            self.toast("تاریخ نامعتبر", "error")
            await self.push_state()

    async def _on_toggle_calendar(self, p):
        self.show_calendar = not self.show_calendar
        if self.show_calendar:
            jy, jm, _ = gregorian_to_jalali_parts(self.current_date)
            self.calendar_year = jy
            self.calendar_month = jm
        await self.push_state()

    async def _on_cal_prev_month(self, p):
        if self.calendar_month and self.calendar_year:
            if self.calendar_month == 1:
                self.calendar_month = 12
                self.calendar_year -= 1
            else:
                self.calendar_month -= 1
        await self.push_state()

    async def _on_cal_next_month(self, p):
        if self.calendar_month and self.calendar_year:
            if self.calendar_month == 12:
                self.calendar_month = 1
                self.calendar_year += 1
            else:
                self.calendar_month += 1
        await self.push_state()

    async def _on_set_search(self, p):
        self.search_query = p.get("q", "")
        await self.push_state()

    # ── tasks ─────────────────────────────────────────────────────────────────

    async def _on_toggle_task(self, p):
        task_id = int(p.get("id", 0))
        if task_id in self.expanded_tasks:
            self.expanded_tasks.discard(task_id)
        else:
            self.expanded_tasks.add(task_id)
        await self.push_state()

    async def _on_add_task(self, p):
        title = p.get("title", "").strip()
        if title:
            task = self.db.add_task(self.current_date, title)
            self.expanded_tasks.add(task.id)
            self.toast("تسک افزوده شد")
        await self.push_state()

    async def _on_delete_task(self, p):
        task_id = int(p.get("id", 0))
        confirmed = await self.app.main_window.dialog(
            toga.ConfirmDialog("حذف تسک", "آیا مطمئن هستید؟")
        )
        if confirmed:
            if self.timer_service.is_running(task_id):
                self._stop_timer_and_save()
            self.db.delete_task(task_id)
            self.expanded_tasks.discard(task_id)
            self.toast("تسک حذف شد")
        await self.push_state()

    async def _on_toggle_star(self, p):
        task_id = int(p.get("id", 0))
        task = self.db.get_task_by_id(task_id)
        if task:
            if task.is_starred:
                self.recurring_svc.unstar_task(task_id, task.recurring_id)
            else:
                self.recurring_svc.star_task(task_id, task.title)
        await self.push_state()

    async def _on_set_useful(self, p):
        task_id = int(p.get("id", 0))
        val = p.get("value")
        if val == "true":
            is_useful = True
        elif val == "false":
            is_useful = False
        else:
            is_useful = None
        self.db.set_useful(task_id, is_useful)
        await self.push_state()

    async def _on_edit_title(self, p):
        task_id = int(p.get("id", 0))
        value = p.get("value", "").strip()
        if value:
            self.db.update_task_title(task_id, value)
        await self.push_state()

    async def _on_set_duration(self, p):
        task_id = int(p.get("id", 0))
        value = p.get("value", "").strip()
        secs = _parse_hms(value)
        if secs is not None:
            self.db.update_duration(task_id, secs)
        else:
            self.toast("فرمت مدت نامعتبر", "error")
        await self.push_state()

    async def _on_set_estimated(self, p):
        task_id = int(p.get("id", 0))
        value = p.get("value", "").strip()
        secs = _parse_hms(value)
        if secs is not None:
            self.db.update_estimated(task_id, secs)
        else:
            self.toast("فرمت تخمین نامعتبر", "error")
        await self.push_state()

    async def _on_copy_task(self, p):
        task_id = int(p.get("id", 0))
        new_task = self.db.copy_task_to_next_day(task_id)
        if new_task:
            self.toast("کپی به فردا انجام شد")
        await self.push_state()

    async def _on_move_task(self, p):
        task_id = int(p.get("id", 0))
        direction = p.get("dir", "up")
        self.db.move_task(task_id, direction)
        await self.push_state()

    # ── timer ─────────────────────────────────────────────────────────────────

    async def _on_start_timer(self, p):
        task_id = int(p.get("id", 0))
        if self.timer_service.is_running(task_id):
            await self.push_state()
            return
        if self.timer_service.active_task_id is not None:
            self._stop_timer_and_save()
        self.timer_service.start(task_id)
        self._persist_active_timer()
        await self.push_state()

    async def _on_stop_timer(self, p):
        self._stop_timer_and_save()
        await self.push_state()

    # ── finance ───────────────────────────────────────────────────────────────

    async def _on_add_finance(self, p):
        entry_type = p.get("type", "expense")
        if entry_type not in ("income", "expense", "investment"):
            entry_type = "expense"
        title = p.get("title", "").strip()
        category = p.get("category", "عمومی")
        try:
            amount = int(float(p.get("amount", "0")))
        except (ValueError, TypeError):
            amount = 0
        if title and amount > 0:
            self.db.add_finance_entry(
                self.current_date, entry_type, title, amount, category
            )
            self.toast("ورود مالی ثبت شد")
        await self.push_state()

    async def _on_edit_finance(self, p):
        entry_id = int(p.get("id", 0))
        entry = self.db.get_finance_entry_by_id(entry_id)
        if not entry:
            await self.push_state()
            return
        title = p.get("title", "").strip()
        category = p.get("category", "عمومی")
        try:
            amount = int(float(p.get("amount", "0")))
        except (ValueError, TypeError):
            amount = 0
        if title and amount > 0:
            self.db.update_finance_entry(
                entry_id, title, amount, entry.entry_type, category
            )
            self.toast("ویرایش شد")
        await self.push_state()

    async def _on_delete_finance(self, p):
        entry_id = int(p.get("id", 0))
        confirmed = await self.app.main_window.dialog(
            toga.ConfirmDialog("حذف ورود مالی", "آیا مطمئن هستید؟")
        )
        if confirmed:
            self.db.delete_finance_entry(entry_id)
            self.toast("حذف شد")
        await self.push_state()

    async def _on_finance_prev_month(self, p):
        if self.finance_month == 1:
            self.finance_month = 12
            self.finance_year -= 1
        else:
            self.finance_month -= 1
        await self.push_state()

    async def _on_finance_next_month(self, p):
        if self.finance_month == 12:
            self.finance_month = 1
            self.finance_year += 1
        else:
            self.finance_month += 1
        await self.push_state()

    async def _on_finance_current_month(self, p):
        today = datetime.date.today()
        self.finance_year = today.year
        self.finance_month = today.month
        await self.push_state()

    async def _on_set_budget(self, p):
        category = p.get("category", "").strip()
        try:
            amount = int(float(p.get("amount", "0")))
        except (ValueError, TypeError):
            amount = 0
        if category:
            self.db.set_budget_limit(category, max(0, amount))
            self.toast("بودجه ذخیره شد")
        await self.push_state()

    async def _on_add_finance_category(self, p):
        from dailyplanner.ui.tokens import FINANCE_CATEGORIES

        name = p.get("name", "").strip()
        if not name:
            await self.push_state()
            return
        existing = set(FINANCE_CATEGORIES) | set(self.db.get_finance_custom_categories())
        if name in existing:
            self.toast("این دسته قبلاً وجود دارد", "error")
        elif self.db.add_finance_custom_category(name):
            self.toast("دسته افزوده شد")
        else:
            self.toast("خطا در افزودن دسته", "error")
        await self.push_state()

    # ── wellness ──────────────────────────────────────────────────────────────

    async def _on_set_sleep(self, p):
        mins = _parse_hm(p.get("value", ""))
        if mins is not None:
            self.db.set_wellness(self.current_date, sleep_minutes=mins, update_sleep=True)
        else:
            self.toast("فرمت ساعت نامعتبر", "error")
        await self.push_state()

    async def _on_set_wake(self, p):
        mins = _parse_hm(p.get("value", ""))
        if mins is not None:
            self.db.set_wellness(self.current_date, wake_minutes=mins, update_wake=True)
        else:
            self.toast("فرمت ساعت نامعتبر", "error")
        await self.push_state()

    async def _on_set_mood(self, p):
        score = int(p.get("score", 0))
        if 1 <= score <= 10:
            self.db.set_wellness(self.current_date, mood_score=score, update_mood=True)
        await self.push_state()

    async def _on_set_note(self, p):
        self.db.set_daily_note(self.current_date, p.get("value", ""))
        # no push — avoid interrupting typing; next action will refresh

    # ── analytics ─────────────────────────────────────────────────────────────

    async def _on_set_period(self, p):
        days = int(p.get("days", 7))
        self.analytics_period = max(1, min(days, 365))
        await self.push_state()

    # ── settings ──────────────────────────────────────────────────────────────

    async def _on_set_theme(self, p):
        theme = p.get("theme", "dark")
        if theme not in ("dark", "light"):
            theme = "dark"
        self.db.set_setting("theme", theme)
        self.toast("تم تغییر کرد")
        await self.push_state()

    async def _on_export_data(self, p):
        data = self.db.export_json()
        payload = json.dumps(data, ensure_ascii=False, indent=2)
        b64 = base64.b64encode(payload.encode("utf-8")).decode("ascii")
        js = f"""
        try {{
            var t = decodeURIComponent(escape(atob('{b64}')));
            if(navigator.clipboard) navigator.clipboard.writeText(t);
            window._exportData = t;
        }} catch(e) {{}}
        """
        try:
            await self.app.webview.evaluate_javascript(js)
        except Exception:
            pass
        self.toast("خروجی JSON آماده است (در حافظه اپ)")

    # ── recurring management ──────────────────────────────────────────────────

    async def _on_delete_recurring(self, p):
        recurring_id = int(p.get("id", 0))
        confirmed = await self.app.main_window.dialog(
            toga.ConfirmDialog("حذف تکرار", "این تسک از لیست تکراری حذف می‌شود.")
        )
        if confirmed:
            self.db.delete_recurring(recurring_id)
            self.toast("حذف شد")
        await self.push_state()


def _parse_hms(text: str) -> Optional[int]:
    try:
        parts = text.strip().split(":")
        if len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        if len(parts) == 2:
            return int(parts[0]) * 3600 + int(parts[1]) * 60
    except (ValueError, IndexError):
        pass
    return None


def _parse_hm(text: str) -> Optional[int]:
    try:
        parts = text.strip().split(":")
        if len(parts) >= 2:
            return int(parts[0]) * 60 + int(parts[1])
    except (ValueError, IndexError):
        pass
    return None
