import json
import sqlite3
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import List, Optional

from dailyplanner.models import DailyTask, DailyWellness, FinanceEntry, Installment, Project, ProjectTask, RecurringTask, date_to_str, str_to_date


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
                entry_type TEXT NOT NULL CHECK(entry_type IN ('income', 'expense', 'investment')),
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

            CREATE TABLE IF NOT EXISTS budget_limits (
                category TEXT PRIMARY KEY,
                monthly_limit INTEGER NOT NULL DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                color TEXT NOT NULL DEFAULT '#5E5CE6',
                deadline TEXT,
                is_done INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS project_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                title TEXT NOT NULL,
                is_done INTEGER NOT NULL DEFAULT 0,
                sort_order INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS installments (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                title      TEXT    NOT NULL,
                amount     INTEGER NOT NULL,
                total_count INTEGER NOT NULL,
                paid_count  INTEGER NOT NULL DEFAULT 0,
                start_date  TEXT    NOT NULL,
                due_day     INTEGER NOT NULL DEFAULT 1,
                created_at  TEXT    NOT NULL
            );

            CREATE TABLE IF NOT EXISTS installment_payments (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                installment_id  INTEGER NOT NULL
                                REFERENCES installments(id) ON DELETE CASCADE,
                payment_date    TEXT NOT NULL,
                created_at      TEXT NOT NULL
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
        if "project_task_id" not in columns:
            self.conn.execute(
                """
                ALTER TABLE daily_tasks ADD COLUMN project_task_id INTEGER
                REFERENCES project_tasks(id) ON DELETE SET NULL
                """
            )

        fin_cols = {
            row[1] for row in self.conn.execute("PRAGMA table_info(finance_entries)")
        }
        if "category" not in fin_cols:
            self.conn.execute(
                "ALTER TABLE finance_entries ADD COLUMN category TEXT NOT NULL DEFAULT 'عمومی'"
            )

        tables = {
            row[0]
            for row in self.conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
        if "budget_limits" not in tables:
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS budget_limits (
                    category TEXT PRIMARY KEY,
                    monthly_limit INTEGER NOT NULL DEFAULT 0
                )
                """
            )

        fin_sql_row = self.conn.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name='finance_entries'"
        ).fetchone()
        fin_sql = fin_sql_row["sql"] if fin_sql_row else ""
        if fin_sql and "'investment'" not in fin_sql:
            self.conn.executescript(
                """
                CREATE TABLE finance_entries_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    entry_type TEXT NOT NULL CHECK(entry_type IN ('income', 'expense', 'investment')),
                    title TEXT NOT NULL,
                    amount INTEGER NOT NULL CHECK(amount > 0),
                    category TEXT NOT NULL DEFAULT 'عمومی'
                );
                INSERT INTO finance_entries_new (id, date, entry_type, title, amount, category)
                SELECT id, date, entry_type, title, amount, category FROM finance_entries;
                DROP TABLE finance_entries;
                ALTER TABLE finance_entries_new RENAME TO finance_entries;
                """
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
                COALESCE(SUM(CASE WHEN entry_type = 'expense' THEN amount END), 0) AS expense,
                COALESCE(SUM(CASE WHEN entry_type = 'investment' THEN amount END), 0) AS investment
            FROM finance_entries WHERE date = ?
            """,
            (date_to_str(d),),
        ).fetchone()
        return int(row["income"]), int(row["expense"]), int(row["investment"])

    def get_finance_balance_until(self, d: date) -> int:
        row = self.conn.execute(
            """
            SELECT COALESCE(
                SUM(
                    CASE
                        WHEN entry_type = 'income' THEN amount
                        WHEN entry_type IN ('expense', 'investment') THEN -amount
                        ELSE 0
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

    def get_finance_entries_for_month(self, year: int, month: int) -> List[FinanceEntry]:
        prefix = f"{year:04d}-{month:02d}"
        rows = self.conn.execute(
            """
            SELECT * FROM finance_entries
            WHERE date LIKE ?
            ORDER BY date, id
            """,
            (f"{prefix}%",),
        ).fetchall()
        return [FinanceEntry.from_row(row) for row in rows]

    def get_finance_monthly_totals(self, year: int, month: int) -> dict:
        prefix = f"{year:04d}-{month:02d}"
        rows = self.conn.execute(
            """
            SELECT category, entry_type, SUM(amount) AS total
            FROM finance_entries
            WHERE date LIKE ?
            GROUP BY category, entry_type
            """,
            (f"{prefix}%",),
        ).fetchall()
        total_income = 0
        total_expense = 0
        total_investment = 0
        by_category: dict = {}
        for row in rows:
            cat = row["category"] or "عمومی"
            if cat not in by_category:
                by_category[cat] = {"income": 0, "expense": 0, "investment": 0}
            amount = int(row["total"])
            entry_type = row["entry_type"]
            if entry_type == "income":
                by_category[cat]["income"] += amount
                total_income += amount
            elif entry_type == "investment":
                by_category[cat]["investment"] += amount
                total_investment += amount
            else:
                by_category[cat]["expense"] += amount
                total_expense += amount
        return {
            "total_income": total_income,
            "total_expense": total_expense,
            "total_investment": total_investment,
            "by_category": by_category,
        }

    def get_finance_daily_series(self, year: int, month: int) -> List[dict]:
        prefix = f"{year:04d}-{month:02d}"
        rows = self.conn.execute(
            """
            SELECT
                date,
                COALESCE(SUM(CASE WHEN entry_type = 'income' THEN amount END), 0) AS income,
                COALESCE(SUM(CASE WHEN entry_type = 'expense' THEN amount END), 0) AS expense,
                COALESCE(SUM(CASE WHEN entry_type = 'investment' THEN amount END), 0) AS investment
            FROM finance_entries
            WHERE date LIKE ?
            GROUP BY date
            ORDER BY date
            """,
            (f"{prefix}%",),
        ).fetchall()
        return [
            {
                "date": row["date"],
                "income": int(row["income"]),
                "expense": int(row["expense"]),
                "investment": int(row["investment"]),
            }
            for row in rows
        ]

    def get_budget_limits(self) -> dict:
        rows = self.conn.execute(
            "SELECT category, monthly_limit FROM budget_limits"
        ).fetchall()
        return {row["category"]: int(row["monthly_limit"]) for row in rows}

    def set_budget_limit(self, category: str, monthly_limit: int):
        self.conn.execute(
            """
            INSERT INTO budget_limits (category, monthly_limit) VALUES (?, ?)
            ON CONFLICT(category) DO UPDATE SET monthly_limit = excluded.monthly_limit
            """,
            (category, monthly_limit),
        )
        self.conn.commit()

    def delete_budget_limit(self, category: str):
        self.conn.execute(
            "DELETE FROM budget_limits WHERE category = ?", (category.strip(),)
        )
        self.conn.commit()

    def get_finance_custom_categories(self) -> List[str]:
        raw = self.get_setting("finance_custom_categories", "[]")
        try:
            data = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return []
        if not isinstance(data, list):
            return []
        return [str(c).strip() for c in data if str(c).strip()]

    def add_finance_custom_category(self, name: str) -> bool:
        name = name.strip()
        if not name:
            return False
        cats = self.get_finance_custom_categories()
        if name in cats:
            return False
        cats.append(name)
        self.set_setting("finance_custom_categories", json.dumps(cats, ensure_ascii=False))
        return True

    def get_finance_summary_for_range(self, start: date, end: date) -> dict:
        row = self.conn.execute(
            """
            SELECT
                COALESCE(SUM(CASE WHEN entry_type = 'income' THEN amount END), 0) AS total_income,
                COALESCE(SUM(CASE WHEN entry_type = 'expense' THEN amount END), 0) AS total_expense,
                COALESCE(SUM(CASE WHEN entry_type = 'investment' THEN amount END), 0) AS total_investment
            FROM finance_entries
            WHERE date >= ? AND date <= ?
            """,
            (date_to_str(start), date_to_str(end)),
        ).fetchone()
        return {
            "total_income": int(row["total_income"]),
            "total_expense": int(row["total_expense"]),
            "total_investment": int(row["total_investment"]),
        }

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
        projects = self.conn.execute("SELECT * FROM projects ORDER BY id").fetchall()
        proj_tasks = self.conn.execute(
            "SELECT * FROM project_tasks ORDER BY project_id, sort_order"
        ).fetchall()
        budgets = self.conn.execute("SELECT * FROM budget_limits").fetchall()
        return {
            "version": 2,
            "tasks": [dict(r) for r in tasks],
            "finance": [dict(r) for r in finance],
            "wellness": [dict(r) for r in wellness],
            "notes": [dict(r) for r in notes],
            "recurring": [dict(r) for r in recurring],
            "settings": {r["key"]: r["value"] for r in settings},
            "projects": [dict(r) for r in projects],
            "project_tasks": [dict(r) for r in proj_tasks],
            "budget_limits": [dict(r) for r in budgets],
        }

    def validate_backup(self, data) -> tuple[bool, str]:
        if not isinstance(data, dict):
            return False, "فرمت فایل نامعتبر است"

        try:
            version = int(data.get("version"))
        except (TypeError, ValueError):
            return False, "نسخه فایل پشتیبانی نمی‌شود"

        if version not in (1, 2):
            return False, "نسخه فایل پشتیبانی نمی‌شود"

        tasks = data.get("tasks")
        if not isinstance(tasks, list):
            return False, "تسک‌ها خراب هستند"
        for t in tasks:
            if not isinstance(t, dict):
                return False, "تسک‌ها خراب هستند"
            if not isinstance(t.get("date"), str) or not isinstance(t.get("title"), str):
                return False, "تسک‌ها خراب هستند"

        finance = data.get("finance")
        if not isinstance(finance, list):
            return False, "ورودی‌های مالی خراب هستند"
        for f in finance:
            if not isinstance(f, dict):
                return False, "ورودی‌های مالی خراب هستند"
            if not isinstance(f.get("date"), str):
                return False, "ورودی‌های مالی خراب هستند"
            if f.get("entry_type") not in ("income", "expense"):
                return False, "ورودی‌های مالی خراب هستند"
            if not isinstance(f.get("title"), str):
                return False, "ورودی‌های مالی خراب هستند"
            try:
                if int(f.get("amount")) <= 0:
                    return False, "ورودی‌های مالی خراب هستند"
            except (TypeError, ValueError):
                return False, "ورودی‌های مالی خراب هستند"

        for key in ("wellness", "notes", "recurring"):
            if not isinstance(data.get(key), list):
                return False, "فرمت فایل نامعتبر است"

        if version == 2:
            projects = data.get("projects")
            if not isinstance(projects, list):
                return False, "پروژه‌ها خراب هستند"
            for p in projects:
                if not isinstance(p, dict) or not isinstance(p.get("title"), str):
                    return False, "پروژه‌ها خراب هستند"

            proj_tasks = data.get("project_tasks")
            if not isinstance(proj_tasks, list):
                return False, "پروژه‌ها خراب هستند"
            for pt in proj_tasks:
                if not isinstance(pt, dict):
                    return False, "پروژه‌ها خراب هستند"
                if not isinstance(pt.get("title"), str) or "project_id" not in pt:
                    return False, "پروژه‌ها خراب هستند"

        for t in tasks[:5]:
            try:
                date.fromisoformat(t["date"])
            except ValueError:
                return False, "تسک‌ها خراب هستند"

        for f in finance[:5]:
            try:
                date.fromisoformat(f["date"])
            except ValueError:
                return False, "ورودی‌های مالی خراب هستند"

        return True, ""

    def import_json(self, data: dict):
        version = int(data.get("version", 1))
        with self.conn:
            self.conn.execute("DELETE FROM daily_tasks")
            self.conn.execute("DELETE FROM finance_entries")
            self.conn.execute("DELETE FROM daily_wellness")
            self.conn.execute("DELETE FROM daily_notes")
            self.conn.execute("DELETE FROM recurring_tasks")
            self.conn.execute("DELETE FROM projects")
            self.conn.execute("DELETE FROM project_tasks")
            self.conn.execute("DELETE FROM budget_limits")
            self.conn.execute("DELETE FROM settings")

            try:
                for tbl in (
                    "daily_tasks",
                    "finance_entries",
                    "recurring_tasks",
                    "projects",
                    "project_tasks",
                ):
                    self.conn.execute(
                        "DELETE FROM sqlite_sequence WHERE name = ?", (tbl,)
                    )
            except Exception:
                pass

            for r in data.get("recurring", []):
                self.conn.execute(
                    "INSERT INTO recurring_tasks (id, title, created_at) VALUES (?,?,?)",
                    (r["id"], r["title"], r.get("created_at", "")),
                )

            if version >= 2:
                for p in data.get("projects", []):
                    self.conn.execute(
                        "INSERT INTO projects (id, title, color, deadline, is_done, created_at)"
                        " VALUES (?,?,?,?,?,?)",
                        (
                            p["id"],
                            p["title"],
                            p.get("color", "#5E5CE6"),
                            p.get("deadline"),
                            int(p.get("is_done", 0)),
                            p.get("created_at", ""),
                        ),
                    )
                for pt in data.get("project_tasks", []):
                    self.conn.execute(
                        "INSERT INTO project_tasks"
                        " (id, project_id, title, is_done, sort_order, created_at)"
                        " VALUES (?,?,?,?,?,?)",
                        (
                            pt["id"],
                            pt["project_id"],
                            pt["title"],
                            int(pt.get("is_done", 0)),
                            int(pt.get("sort_order", 0)),
                            pt.get("created_at", ""),
                        ),
                    )

            for t in data.get("tasks", []):
                self.conn.execute(
                    "INSERT INTO daily_tasks"
                    " (id, date, title, duration_seconds, estimated_seconds,"
                    "  is_useful, recurring_id, sort_order, project_task_id)"
                    " VALUES (?,?,?,?,?,?,?,?,?)",
                    (
                        t["id"],
                        t["date"],
                        t["title"],
                        int(t.get("duration_seconds", 0)),
                        int(t.get("estimated_seconds", 0)),
                        t.get("is_useful"),
                        t.get("recurring_id"),
                        int(t.get("sort_order", 0)),
                        t.get("project_task_id"),
                    ),
                )

            for f in data.get("finance", []):
                self.conn.execute(
                    "INSERT INTO finance_entries (id, date, entry_type, title, amount, category)"
                    " VALUES (?,?,?,?,?,?)",
                    (
                        f["id"],
                        f["date"],
                        f["entry_type"],
                        f["title"],
                        int(f["amount"]),
                        f.get("category", "عمومی"),
                    ),
                )

            for w in data.get("wellness", []):
                self.conn.execute(
                    "INSERT INTO daily_wellness (date, sleep_minutes, wake_minutes, mood_score)"
                    " VALUES (?,?,?,?)",
                    (
                        w["date"],
                        w.get("sleep_minutes"),
                        w.get("wake_minutes"),
                        w.get("mood_score"),
                    ),
                )

            for n in data.get("notes", []):
                self.conn.execute(
                    "INSERT INTO daily_notes (date, note) VALUES (?,?)",
                    (n["date"], n.get("note", "")),
                )

            if version >= 2:
                for b in data.get("budget_limits", []):
                    self.conn.execute(
                        "INSERT INTO budget_limits (category, monthly_limit) VALUES (?,?)",
                        (b["category"], int(b.get("monthly_limit", 0))),
                    )

            for key, value in data.get("settings", {}).items():
                self.conn.execute(
                    "INSERT INTO settings (key, value) VALUES (?,?)"
                    " ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                    (key, value),
                )

    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None

    # ── projects ──────────────────────────────────────────────────────────────

    def get_all_projects(self) -> List[Project]:
        rows = self.conn.execute(
            "SELECT * FROM projects ORDER BY is_done ASC, id DESC"
        ).fetchall()
        return [Project.from_row(row) for row in rows]

    def get_project_by_id(self, project_id: int) -> Optional[Project]:
        row = self.conn.execute(
            "SELECT * FROM projects WHERE id = ?", (project_id,)
        ).fetchone()
        if row is None:
            return None
        return Project.from_row(row)

    def create_project(
        self, title: str, color: str, deadline: Optional[str]
    ) -> Project:
        now = datetime.now().isoformat()
        cursor = self.conn.execute(
            """
            INSERT INTO projects (title, color, deadline, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (title.strip(), color, deadline, now),
        )
        self.conn.commit()
        return self.get_project_by_id(cursor.lastrowid)

    def update_project(
        self, project_id: int, title: str, color: str, deadline: Optional[str]
    ):
        self.conn.execute(
            """
            UPDATE projects SET title = ?, color = ?, deadline = ?
            WHERE id = ?
            """,
            (title.strip(), color, deadline, project_id),
        )
        self.conn.commit()

    def mark_project_done(self, project_id: int, is_done: bool):
        self.conn.execute(
            "UPDATE projects SET is_done = ? WHERE id = ?",
            (1 if is_done else 0, project_id),
        )
        self.conn.commit()

    def delete_project(self, project_id: int):
        self.conn.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        self.conn.commit()

    def get_project_tasks(self, project_id: int) -> List[ProjectTask]:
        rows = self.conn.execute(
            """
            SELECT * FROM project_tasks WHERE project_id = ?
            ORDER BY is_done ASC, sort_order ASC, id ASC
            """,
            (project_id,),
        ).fetchall()
        return [ProjectTask.from_row(row) for row in rows]

    def get_project_task_by_id(self, task_id: int) -> Optional[ProjectTask]:
        row = self.conn.execute(
            "SELECT * FROM project_tasks WHERE id = ?", (task_id,)
        ).fetchone()
        if row is None:
            return None
        return ProjectTask.from_row(row)

    def add_project_task(self, project_id: int, title: str) -> ProjectTask:
        row = self.conn.execute(
            """
            SELECT COALESCE(MAX(sort_order), -1) + 1 AS n
            FROM project_tasks WHERE project_id = ?
            """,
            (project_id,),
        ).fetchone()
        sort_order = int(row["n"])
        now = datetime.now().isoformat()
        cursor = self.conn.execute(
            """
            INSERT INTO project_tasks (project_id, title, sort_order, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (project_id, title.strip(), sort_order, now),
        )
        self.conn.commit()
        return self.get_project_task_by_id(cursor.lastrowid)

    def toggle_project_task(self, task_id: int) -> ProjectTask:
        task = self.get_project_task_by_id(task_id)
        if task is None:
            raise ValueError(f"project task {task_id} not found")
        new_done = 0 if task.is_done else 1
        self.conn.execute(
            "UPDATE project_tasks SET is_done = ? WHERE id = ?",
            (new_done, task_id),
        )
        self.conn.commit()
        return self.get_project_task_by_id(task_id)

    def delete_project_task(self, task_id: int):
        self.conn.execute("DELETE FROM project_tasks WHERE id = ?", (task_id,))
        self.conn.commit()

    def edit_project_task_title(self, task_id: int, title: str):
        self.conn.execute(
            "UPDATE project_tasks SET title = ? WHERE id = ?",
            (title.strip(), task_id),
        )
        self.conn.commit()

    def get_project_stats(self, project_id: int) -> dict:
        row = self.conn.execute(
            """
            SELECT COUNT(*) AS total, COALESCE(SUM(is_done), 0) AS done
            FROM project_tasks WHERE project_id = ?
            """,
            (project_id,),
        ).fetchone()
        total = int(row["total"])
        done = int(row["done"])
        progress = int(done / total * 100) if total > 0 else 0
        return {"total": total, "done": done, "progress": progress}

    def get_daily_tasks_for_project_task(
        self, project_task_id: int
    ) -> List[DailyTask]:
        rows = self.conn.execute(
            "SELECT * FROM daily_tasks WHERE project_task_id = ?",
            (project_task_id,),
        ).fetchall()
        return [DailyTask.from_row(row) for row in rows]

    def create_daily_task_from_project(
        self, project_task_id: int, d: date
    ) -> DailyTask:
        pt = self.get_project_task_by_id(project_task_id)
        if pt is None:
            raise ValueError(f"project task {project_task_id} not found")
        new_task = self.add_task(d, pt.title)
        self.conn.execute(
            "UPDATE daily_tasks SET project_task_id = ? WHERE id = ?",
            (project_task_id, new_task.id),
        )
        self.conn.commit()
        return self.get_task_by_id(new_task.id)

    # ── installments ──────────────────────────────────────────────────────────

    def get_all_installments(self) -> List[Installment]:
        rows = self.conn.execute(
            "SELECT * FROM installments ORDER BY (paid_count >= total_count) ASC, id ASC"
        ).fetchall()
        return [Installment.from_row(r) for r in rows]

    def get_installment_by_id(self, inst_id: int) -> Optional[Installment]:
        row = self.conn.execute(
            "SELECT * FROM installments WHERE id = ?", (inst_id,)
        ).fetchone()
        return Installment.from_row(row) if row else None

    def add_installment(
        self, title: str, amount: int, total_count: int,
        start_date: str, due_day: int
    ) -> Installment:
        now = datetime.now().isoformat()
        cursor = self.conn.execute(
            "INSERT INTO installments (title, amount, total_count, start_date, due_day, created_at)"
            " VALUES (?,?,?,?,?,?)",
            (title.strip(), amount, total_count, start_date, due_day, now),
        )
        self.conn.commit()
        return self.get_installment_by_id(cursor.lastrowid)

    def edit_installment(
        self, inst_id: int, title: str, amount: int,
        total_count: int, start_date: str, due_day: int
    ):
        self.conn.execute(
            "UPDATE installments SET title=?, amount=?, total_count=?,"
            " start_date=?, due_day=? WHERE id=?",
            (title.strip(), amount, total_count, start_date, due_day, inst_id),
        )
        self.conn.commit()

    def delete_installment(self, inst_id: int):
        self.conn.execute("DELETE FROM installments WHERE id=?", (inst_id,))
        self.conn.commit()

    def pay_installment(self, inst_id: int) -> Optional[Installment]:
        """Record one payment. Returns updated installment or None if already settled."""
        inst = self.get_installment_by_id(inst_id)
        if inst is None or inst.is_settled:
            return None
        now_str = datetime.now().isoformat()
        today = datetime.now().strftime("%Y-%m-%d")
        self.conn.execute(
            "UPDATE installments SET paid_count = paid_count + 1 WHERE id = ?",
            (inst_id,),
        )
        self.conn.execute(
            "INSERT INTO installment_payments (installment_id, payment_date, created_at)"
            " VALUES (?,?,?)",
            (inst_id, today, now_str),
        )
        self.conn.commit()
        return self.get_installment_by_id(inst_id)

    def is_paid_this_month(self, inst_id: int, year: int, month: int) -> bool:
        """Check if this installment was paid in the given Gregorian year/month."""
        prefix = f"{year:04d}-{month:02d}"
        row = self.conn.execute(
            "SELECT 1 FROM installment_payments"
            " WHERE installment_id=? AND payment_date LIKE ?",
            (inst_id, prefix + "%"),
        ).fetchone()
        return row is not None

    def get_installments_summary_for_month(self, year: int, month: int) -> dict:
        """Returns active installments with their payment status for the given month."""
        installments = self.get_all_installments()
        active = [i for i in installments if not i.is_settled]
        result = []
        for inst in active:
            paid_month = self.is_paid_this_month(inst.id, year, month)
            result.append({
                "installment": inst,
                "paid_this_month": paid_month,
            })
        total_due = sum(i.amount for i in active)
        total_unpaid = sum(
            i["installment"].amount for i in result if not i["paid_this_month"]
        )
        return {
            "items": result,
            "total_due": total_due,
            "total_unpaid": total_unpaid,
        }
