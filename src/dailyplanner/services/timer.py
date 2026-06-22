import time
from typing import Callable, Optional


class TimerService:
    def __init__(self):
        self._active_task_id: Optional[int] = None
        self._start_epoch: Optional[float] = None
        self._on_tick: Optional[Callable[[int, int], None]] = None

    @property
    def active_task_id(self) -> Optional[int]:
        return self._active_task_id

    @property
    def start_epoch(self) -> Optional[float]:
        return self._start_epoch

    def is_running(self, task_id: int) -> bool:
        return self._active_task_id == task_id

    def set_on_tick(self, callback: Callable[[int, int], None]):
        self._on_tick = callback

    def start(self, task_id: int) -> Optional[int]:
        """Start timer. Returns previous task id if another was running."""
        previous = self._active_task_id
        self._active_task_id = task_id
        self._start_epoch = time.time()
        return previous if previous != task_id else None

    def restore(self, task_id: int, start_epoch: float) -> None:
        """Resume a timer persisted from a previous app session."""
        self._active_task_id = task_id
        self._start_epoch = start_epoch

    def stop(self) -> tuple:
        """Stop timer. Returns (task_id, elapsed_seconds)."""
        if self._active_task_id is None or self._start_epoch is None:
            return None, 0
        elapsed = self.get_elapsed()
        task_id = self._active_task_id
        self._active_task_id = None
        self._start_epoch = None
        return task_id, elapsed

    def get_elapsed(self) -> int:
        if self._active_task_id is None or self._start_epoch is None:
            return 0
        return max(0, int(time.time() - self._start_epoch))

    def get_display_seconds(self, task_id: int, base_seconds: int) -> int:
        if self.is_running(task_id):
            return base_seconds + self.get_elapsed()
        return base_seconds

    def tick(self):
        if self._active_task_id and self._on_tick:
            self._on_tick(self._active_task_id, self.get_elapsed())
