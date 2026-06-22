from datetime import date

from dailyplanner.database import Database


class RecurringService:
    def __init__(self, db: Database):
        self.db = db

    def ensure_daily_tasks(self, d: date):
        existing = self.db.get_recurring_ids_for_date(d)
        for recurring in self.db.get_all_recurring():
            if recurring.id not in existing:
                self.db.create_recurring_instance(recurring.id, recurring.title, d)

    def star_task(self, task_id: int, title: str) -> int:
        recurring = self.db.create_recurring(title)
        self.db.link_task_to_recurring(task_id, recurring.id)
        return recurring.id

    def unstar_task(self, task_id: int, recurring_id: int):
        self.db.unlink_task_recurring(task_id)
        if self.db.count_tasks_with_recurring(recurring_id, exclude_task_id=task_id) == 0:
            self.db.delete_recurring(recurring_id)
