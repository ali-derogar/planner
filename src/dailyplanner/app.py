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
        self._ui_loaded = False

        self.webview = toga.WebView(style=Pack(flex=1))
        self.webview.on_webview_load = self._on_webview_load

        # Window (not MainWindow) hides Android's native ActionBar on mobile.
        self.main_window = toga.Window(title="")
        self.main_window.content = self.webview
        self.main_window.on_show = self._on_main_window_show
        hide_android_action_bar(self.main_window)
        self.main_window.show()

        self.on_running = self._on_running

    def _on_webview_load(self, webview, **kwargs):
        asyncio.create_task(self.handler.push_state())

    def _on_main_window_show(self, window, **kwargs):
        hide_android_action_bar(self.main_window)
        if self._ui_loaded:
            return
        self._ui_loaded = True
        print("[app] loading shell")
        self.handler.load_shell()
        asyncio.create_task(self.handler.push_state())

    def _on_running(self, app, **kwargs):
        if not self._ui_loaded:
            print("[app] on_running fallback load")
            self._ui_loaded = True
            self.handler.load_shell()
            asyncio.create_task(self.handler.push_state())
        asyncio.create_task(self.handler.poll_loop(self))
        asyncio.create_task(self.handler.timer_update_loop(self))

    def on_exit(self, widget=None, **kwargs):
        # Stop any running timer and save elapsed before exit
        task_id, elapsed = self.handler.timer_service.stop()
        if task_id and elapsed > 0:
            self.db.add_duration(task_id, elapsed)
        self.db.close()
        return True


def main():
    return DailyPlannerApp(
        "Daily Planner",
        "com.taskplanner.dailyplanner",
    )
