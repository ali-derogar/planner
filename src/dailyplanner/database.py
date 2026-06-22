import sqlite3
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import List, Optional

from dailyplanner.models import DailyTask, DailyWellness, FinanceEntry, RecurringTask, date_to_str, str_to_date


DEFAULT_SETTINGS = {"theme": "dark"}


class Database:
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = str(Path.home() / "tasks.db")
        self.db_path = db_path
        self._conn: Optional[sqlite3.Connection] = None

    @property
    def conn(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path)
            self._conn.row_factory = sqlite3.Row
            self._conn.execute("PRAGMA foreign_keys = ON")
            self._init_schema()
        return self._conn

    def _init_schema(self):
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS recurring_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS daily_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                title TEXT NOT NULL,
                duration_seconds INTEGER NOT NULL DEFAULT 0,
                estimated_seconds INTEGER NOT NULL DEFAULT 0,
                is_useful INTEGER,
                recurring_id INTEGER REFERENCES recurring_tasks(id) ON DELETE SET NULL,
                UNIQUE(date, recurring_id)
            );

            CREATE TABLE IF NOT EXISTS finance_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                entry_type TEXT NOT NULL CHECK(entry_type IN ('income', 'expense')),
                title TEXT NOT NULL,
                amount INTEGER NOT NULL CHECK(amount > 0)
            );

            CREATE TABLE IF NOT EXISTS daily_wellness (
                date TEXT PRIMARY KEY,
                sleep_minutes INTEGER,
                wake_minutes INTEGER,
                mood_score INTEGER CHECK(mood_score IS NULL OR (mood_score >= 1 AND mood_score <= 10))
            );

            CREATE TABLE IF NOT EXISTS daily_notes (
                date TEXT PRIMARY KEY,
                note TEXT NOT NULL DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
            """
        )
        self.conn.commit()
        self._migrate_schema()

    def _migrate_schema(self):
        columns = {
            row[1] for row in self.conn.execute("PRAGMA table_info(daily_tasks)")
        }
        if "estimated_seconds" not in columns:
            self.conn.execute(
                "ALTER TABLE daily_tasks ADD COLUMN estimated_seconds INTEGER NOT NULL DEFAULT 0"
            )
        if "sort_order" not in columns:
            self.conn.execute(
                "ALTER TABLE daily_tasks ADD COLUMN sort_order INTEGER NOT NULL DEFAULT 0"
            )

        fin_cols = {
            row[1] for row in self.conn.execute("PRAGMA table_info(finance_entries)")
        }
        if "category" not in fin_cols:
            self.conn.execute(
                "ALTER TABLE finance_entries ADD COLUMN category TEXT NOT NULL DEFAULT 'عمومی'"
            )
        self.conn.commit()

    def get_tasks_for_date(self, d: date) -> List[DailyTask]:
        rows = self.conn.execute(
            "SELECT * FROM daily_tasks WHERE date = ? ORDER BY sort_order, id",
            (date_to_str(d),),
        ).fetchall()
        return [DailyTask.from_row(row) for row in rows]

    def add_task(self, d: date, title: str) -> DailyTask:
        row = self.conn.execute(
            "SELECT COALESCE(MAX(sort_order), -1) + 1 AS n FROM daily_tasks WHERE date = ?",
            (date_to_str(d),),
        ).fetchone()
        sort_order = int(row["n"])
        cursor = self.conn.execute(
            "INSERT INTO daily_tasks (date, title, sort_order) VALUES (?, ?, ?)",
            (date_to_str(d), title.strip(), sort_order),
        )
        self.conn.commit()
        return self.get_task_by_id(cursor.lastrowid)

    def get_task_by_id(self, task_id: int) -> Optional[DailyTask]:
        row = self.conn.execute(
            "SELECT * FROM daily_tasks WHERE id = ?", (task_id,)
        ).fetchone()
        if row is None:
            return None
        return DailyTask.from_row(row)

    def count_tasks_with_recurring(self, recurring_id: int, exclude_task_id: int = 0) -> int:
        row = self.conn.execute(
            "SELECT COUNT(*) AS c FROM daily_tasks WHERE recurring_id = ? AND id != ?",
            (recurring_id, exclude_task_id),
        ).fetchone()
        return row["c"]

    def get_useful_totals(self, d: date) -> tuple:
        row = self.conn.execute(
            """
            SELECT
                COALESCE(SUM(CASE WHEN is_useful = 1 THEN duration_seconds END), 0) AS useful,
                COALESCE(SUM(CASE WHEN is_useful = 0 THEN duration_seconds END), 0) AS not_useful
            FROM daily_tasks WHERE date = ?
            """,
            (date_to_str(d),),
        ).fetchone()
        return int(row["useful"]), int(row["not_useful"])

    def update_duration(self, task_id: int, duration_seconds: int):
        self.conn.execute(
            "UPDATE daily_tasks SET duration_seconds = ? WHERE id = ?",
            (duration_seconds, task_id),
        )
        self.conn.commit()

    def update_estimated(self, task_id: int, estimated_seconds: int):
        self.conn.execute(
            "UPDATE daily_tasks SET estimated_seconds = ? WHERE id = ?",
            (estimated_seconds, task_id),
        )
        self.conn.commit()

    def add_duration(self, task_id: int, seconds: int):
        self.conn.execute(
            "UPDATE daily_tasks SET duration_seconds = duration_seconds + ? WHERE id = ?",
            (seconds, task_id),
        )
        self.conn.commit()

    def set_useful(self, task_id: int, is_useful: Optional[bool]):
        value = None
        if is_useful is not None:
            value = 1 if is_useful else 0
        self.conn.execute(
            "UPDATE daily_tasks SET is_useful = ? WHERE id = ?",
            (value, task_id),
        )
        self.conn.commit()

    def move_task(self, task_id: int, direction: str):
        task = self.get_task_by_id(task_id)
        if not task:
            return
        tasks = self.get_tasks_for_date(str_to_date(task.date))
        ids = [t.id for t in tasks]
        idx = ids.index(task_id)
        swap_idx = idx - 1 if direction == "up" else idx + 1
        if swap_idx < 0 or swap_idx >= len(ids):
            return
        other_id = ids[swap_idx]
        other = self.get_task_by_id(other_id)
        self.conn.execute(
            "UPDATE daily_tasks SET sort_order = ? WHERE id = ?",
            (other.sort_order, task_id),
        )
        self.conn.execute(
            "UPDATE daily_tasks SET sort_order = ? WHERE id = ?",
            (task.sort_order, other_id),
        )
        self.conn.commit()

    def copy_task_to_next_day(self, task_id: int) -> Optional[DailyTask]:
        task = self.get_task_by_id(task_id)
        if not task:
            return None
        d = str_to_date(task.date) + timedelta(days=1)
        new_task = self.add_task(d, task.title)
        if task.estimated_seconds:
            self.update_estimated(new_task.id, task.estimated_seconds)
            new_task = self.get_task_by_id(new_task.id)
        return new_task

    def delete_task(self, task_id: int):
        self.conn.execute("DELETE FROM daily_tasks WHERE id = ?", (task_id,))
        self.conn.commit()

    def get_all_recurring(self) -> List[RecurringTask]:
        rows = self.conn.execute(
            "SELECT * FROM recurring_tasks ORDER BY id"
        ).fetchall()
        return [
            RecurringTask(id=row["id"], title=row["title"], created_at=row["created_at"])
            for row in rows
        ]

    def create_recurring(self, title: str) -> RecurringTask:
        now = datetime.now().isoformat()
        cursor = self.conn.execute(
            "INSERT INTO recurring_tasks (title, created_at) VALUES (?, ?)",
            (title, now),
        )
        self.conn.commit()
        row = self.conn.execute(
            "SELECT * FROM recurring_tasks WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()
        return RecurringTask(id=row["id"], title=row["title"], created_at=row["created_at"])

    def delete_recurring(self, recurring_id: int):
        self.conn.execute("DELETE FROM recurring_tasks WHERE id = ?", (recurring_id,))
        self.conn.commit()

    def link_task_to_recurring(self, task_id: int, recurring_id: int):
        self.conn.execute(
            "UPDATE daily_tasks SET recurring_id = ? WHERE id = ?",
            (recurring_id, task_id),
        )
        self.conn.commit()

    def unlink_task_recurring(self, task_id: int):
        self.conn.execute(
            "UPDATE daily_tasks SET recurring_id = NULL WHERE id = ?",
            (task_id,),
        )
        self.conn.commit()

    def has_recurring_task_for_date(self, recurring_id: int, d: date) -> bool:
        row = self.conn.execute(
            "SELECT 1 FROM daily_tasks WHERE recurring_id = ? AND date = ?",
            (recurring_id, date_to_str(d)),
        ).fetchone()
        return row is not None

    def get_recurring_ids_for_date(self, d: date) -> set:
        rows = self.conn.execute(
            "SELECT recurring_id FROM daily_tasks WHERE date = ? AND recurring_id IS NOT NULL",
            (date_to_str(d),),
        ).fetchall()
        return {row["recurring_id"] for row in rows}

    def create_recurring_instance(self, recurring_id: int, title: str, d: date) -> DailyTask:
        cursor = self.conn.execute(
            "INSERT INTO daily_tasks (date, title, recurring_id) VALUES (?, ?, ?)",
            (date_to_str(d), title, recurring_id),
        )
        self.conn.commit()
        return self.get_task_by_id(cursor.lastrowid)

    def get_finance_entries_for_date(self, d: date) -> List[FinanceEntry]:
        rows = self.conn.execute(
            """
            SELECT * FROM finance_entries
            WHERE date = ?
            ORDER BY id
            """,
            (date_to_str(d),),
        ).fetchall()
        return [FinanceEntry.from_row(row) for row in rows]

    def add_finance_entry(
        self, d: date, entry_type: str, title: str, amount: int, category: str = "عمومی"
    ) -> FinanceEntry:
        cursor = self.conn.execute(
            """
            INSERT INTO finance_entries (date, entry_type, title, amount, category)
            VALUES (?, ?, ?, ?, ?)
            """,
            (date_to_str(d), entry_type, title.strip(), amount, category or "عمومی"),
        )
        self.conn.commit()
        return self.get_finance_entry_by_id(cursor.lastrowid)

    def update_finance_entry(
        self,
        entry_id: int,
        title: str,
        amount: int,
        entry_type: str,
        category: str = "عمومی",
    ):
        self.conn.execute(
            """
            UPDATE finance_entries
            SET title = ?, amount = ?, entry_type = ?, category = ?
            WHERE id = ?
            """,
            (title.strip(), amount, entry_type, category or "عمومی", entry_id),
        )
        self.conn.commit()

    def get_finance_entry_by_id(self, entry_id: int) -> Optional[FinanceEntry]:
        row = self.conn.execute(
            "SELECT * FROM finance_entries WHERE id = ?", (entry_id,)
        ).fetchone()
        if row is None:
            return None
        return FinanceEntry.from_row(row)

    def delete_finance_entry(self, entry_id: int):
        self.conn.execute("DELETE FROM finance_entries WHERE id = ?", (entry_id,))
        self.conn.commit()

    def get_finance_daily_totals(self, d: date) -> tuple:
        row = self.conn.execute(
            """
            SELECT
                COALESCE(SUM(CASE WHEN entry_type = 'income' THEN amount END), 0) AS income,
                COALESCE(SUM(CASE WHEN entry_type = 'expense' THEN amount END), 0) AS expense
            FROM finance_entries WHERE date = ?
            """,
            (date_to_str(d),),
        ).fetchone()
        return int(row["income"]), int(row["expense"])

    def get_finance_balance_until(self, d: date) -> int:
        row = self.conn.execute(
            """
            SELECT COALESCE(
                SUM(
                    CASE
                        WHEN entry_type = 'income' THEN amount
                        ELSE -amount
                    END
                ),
                0
            ) AS balance
            FROM finance_entries WHERE date <= ?
            """,
            (date_to_str(d),),
        ).fetchone()
        return int(row["balance"])

    def get_wellness(self, d: date) -> Optional[DailyWellness]:
        row = self.conn.execute(
            "SELECT * FROM daily_wellness WHERE date = ?", (date_to_str(d),)
        ).fetchone()
        if row is None:
            return None
        return DailyWellness.from_row(row)

    def set_wellness(
        self,
        d: date,
        sleep_minutes: Optional[int] = None,
        wake_minutes: Optional[int] = None,
        mood_score: Optional[int] = None,
        *,
        update_sleep: bool = False,
        update_wake: bool = False,
        update_mood: bool = False,
    ) -> DailyWellness:
        existing = self.get_wellness(d)
        date_str = date_to_str(d)
        if existing is None:
            self.conn.execute(
                """
                INSERT INTO daily_wellness (date, sleep_minutes, wake_minutes, mood_score)
                VALUES (?, ?, ?, ?)
                """,
                (
                    date_str,
                    sleep_minutes if update_sleep else None,
                    wake_minutes if update_wake else None,
                    mood_score if update_mood else None,
                ),
            )
        else:
            new_sleep = sleep_minutes if update_sleep else existing.sleep_minutes
            new_wake = wake_minutes if update_wake else existing.wake_minutes
            new_mood = mood_score if update_mood else existing.mood_score
            self.conn.execute(
                """
                UPDATE daily_wellness
                SET sleep_minutes = ?, wake_minutes = ?, mood_score = ?
                WHERE date = ?
                """,
                (new_sleep, new_wake, new_mood, date_str),
            )
        self.conn.commit()
        return self.get_wellness(d)

    def update_task_title(self, task_id: int, title: str):
        self.conn.execute(
            "UPDATE daily_tasks SET title = ? WHERE id = ?",
            (title.strip(), task_id),
        )
        self.conn.commit()

    def get_tasks_summary_for_range(self, start: date, end: date) -> List[dict]:
        rows = self.conn.execute(
            """
            SELECT
                date,
                COALESCE(SUM(CASE WHEN is_useful = 1 THEN duration_seconds END), 0) AS useful,
                COALESCE(SUM(CASE WHEN is_useful = 0 THEN duration_seconds END), 0) AS not_useful,
                COALESCE(SUM(duration_seconds), 0) AS total,
                COUNT(*) AS task_count
            FROM daily_tasks
            WHERE date >= ? AND date <= ?
            GROUP BY date
            ORDER BY date
            """,
            (date_to_str(start), date_to_str(end)),
        ).fetchall()
        return [dict(row) for row in rows]

    def get_finance_summary_for_range(self, start: date, end: date) -> dict:
        row = self.conn.execute(
            """
            SELECT
                COALESCE(SUM(CASE WHEN entry_type = 'income' THEN amount END), 0) AS total_income,
                COALESCE(SUM(CASE WHEN entry_type = 'expense' THEN amount END), 0) AS total_expense
            FROM finance_entries
            WHERE date >= ? AND date <= ?
            """,
            (date_to_str(start), date_to_str(end)),
        ).fetchone()
        return {"total_income": int(row["total_income"]), "total_expense": int(row["total_expense"])}

    def get_wellness_for_range(self, start: date, end: date) -> List[DailyWellness]:
        rows = self.conn.execute(
            "SELECT * FROM daily_wellness WHERE date >= ? AND date <= ? ORDER BY date",
            (date_to_str(start), date_to_str(end)),
        ).fetchall()
        return [DailyWellness.from_row(row) for row in rows]

    def get_daily_note(self, d: date) -> str:
        row = self.conn.execute(
            "SELECT note FROM daily_notes WHERE date = ?", (date_to_str(d),)
        ).fetchone()
        return row["note"] if row else ""

    def set_daily_note(self, d: date, note: str):
        date_str = date_to_str(d)
        self.conn.execute(
            """
            INSERT INTO daily_notes (date, note) VALUES (?, ?)
            ON CONFLICT(date) DO UPDATE SET note = excluded.note
            """,
            (date_str, note.strip()),
        )
        self.conn.commit()

    def get_setting(self, key: str, default: str = "") -> str:
        row = self.conn.execute(
            "SELECT value FROM settings WHERE key = ?", (key,)
        ).fetchone()
        return row["value"] if row else default

    def set_setting(self, key: str, value: str):
        self.conn.execute(
            """
            INSERT INTO settings (key, value) VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value
            """,
            (key, value),
        )
        self.conn.commit()

    def delete_setting(self, key: str):
        self.conn.execute("DELETE FROM settings WHERE key = ?", (key,))
        self.conn.commit()

    def get_active_timer(self) -> Optional[tuple[int, float]]:
        task_id_raw = self.get_setting("active_timer_task_id")
        started_raw = self.get_setting("active_timer_started_at")
        if not task_id_raw or not started_raw:
            return None
        try:
            return int(task_id_raw), float(started_raw)
        except (TypeError, ValueError):
            return None

    def set_active_timer(self, task_id: int, started_at: float):
        self.set_setting("active_timer_task_id", str(task_id))
        self.set_setting("active_timer_started_at", repr(started_at))

    def clear_active_timer(self):
        self.delete_setting("active_timer_task_id")
        self.delete_setting("active_timer_started_at")

    def export_json(self) -> dict:
        tasks = self.conn.execute("SELECT * FROM daily_tasks ORDER BY date, sort_order").fetchall()
        finance = self.conn.execute("SELECT * FROM finance_entries ORDER BY date").fetchall()
        wellness = self.conn.execute("SELECT * FROM daily_wellness ORDER BY date").fetchall()
        notes = self.conn.execute("SELECT * FROM daily_notes ORDER BY date").fetchall()
        recurring = self.conn.execute("SELECT * FROM recurring_tasks ORDER BY id").fetchall()
        settings = self.conn.execute("SELECT * FROM settings").fetchall()
        return {
            "version": 1,
            "tasks": [dict(r) for r in tasks],
            "finance": [dict(r) for r in finance],
            "wellness": [dict(r) for r in wellness],
            "notes": [dict(r) for r in notes],
            "recurring": [dict(r) for r in recurring],
            "settings": {r["key"]: r["value"] for r in settings},
        }

    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None
