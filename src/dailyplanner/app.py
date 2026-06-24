import asyncio
import toga
from toga.style import Pack

from dailyplanner.database import Database
from dailyplanner.utils.platform import hide_android_action_bar
from dailyplanner.webview_handler import WebViewHandler


class DailyPlannerApp(toga.App):

    def startup(self):
        self.db = Database(str(self.paths.data / "tasks.db"))
        self.handler = WebViewHandler(self)
        self._poll_started = False

        self.webview = toga.WebView(style=Pack(flex=1))
        self.webview.on_webview_load = self._on_webview_load

        # Window (not MainWindow) hides Android's native ActionBar on mobile.
        self.main_window = toga.Window(title="")
        self.main_window.content = self.webview
        self.main_window.on_show = self._on_main_window_show
        hide_android_action_bar(self.main_window)
        self.main_window.show()

        self.on_running = self._on_running

    def _ensure_shell(self):
        if self.handler._shell_requested:
            return
        print("[app] loading shell")
        self.handler.load_shell()

    def _start_background_loops(self):
        if self._poll_started:
            return
        self._poll_started = True
        print("[app] starting JS bridge loops")
        asyncio.create_task(self.handler.poll_loop(self))
        asyncio.create_task(self.handler.timer_update_loop(self))

    def _on_webview_load(self, webview, **kwargs):
        # Ignore the blank page that fires before load_shell() navigates to the SPA.
        if not self.handler._shell_loaded:
            return
        asyncio.create_task(self._on_webview_ready())

    async def _on_webview_ready(self):
        await self.handler.push_state()
        self._start_background_loops()

    def _on_main_window_show(self, window, **kwargs):
        hide_android_action_bar(self.main_window)
        self._ensure_shell()

    def _on_running(self, app, **kwargs):
        self._ensure_shell()
        asyncio.create_task(self._startup_fallback())

    async def _startup_fallback(self):
        """Android sometimes skips on_webview_load — don't leave buttons dead."""
        await asyncio.sleep(3.0)
        self._start_background_loops()
        if self.handler._shell_loaded:
            await self.handler.push_state()

    def on_exit(self, widget=None, **kwargs):
        try:
            asyncio.get_event_loop().run_until_complete(self.handler.flush_pending_js())
        except Exception:
            pass
        self.db.close()
        return True


def main():
    return DailyPlannerApp(
        "Daily Planner",
        "com.taskplanner.dailyplanner",
    )
