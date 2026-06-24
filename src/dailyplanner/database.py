import json
import sqlite3
import time
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import List, Optional

from dailyplanner.models import DailyTask, DailyWellness, FinanceEntry, ImportantDate, Installment, Project, ProjectTask, RecurringTask, date_to_str, str_to_date


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

            CREATE TABLE IF NOT EXISTS important_dates (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                title        TEXT    NOT NULL,
                date         TEXT    NOT NULL,
                category     TEXT    NOT NULL DEFAULT 'سایر',
                notes        TEXT    NOT NULL DEFAULT '',
                repeat_type  TEXT    NOT NULL DEFAULT 'none',
                repeat_months INTEGER NOT NULL DEFAULT 0,
                created_at   TEXT    NOT NULL
            );

            CREATE TABLE IF NOT EXISTS tracking_sessions (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                date        TEXT NOT NULL,
                started_at  REAL NOT NULL,
                ended_at    REAL,
                created_at  TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS tracking_intervals (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id    INTEGER NOT NULL REFERENCES tracking_sessions(id),
                started_at    REAL NOT NULL,
                ended_at      REAL,
                label         TEXT NOT NULL DEFAULT '',
                duration_secs INTEGER,
                is_useful     INTEGER
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

        track_cols = {
            row[1] for row in self.conn.execute("PRAGMA table_info(tracking_intervals)")
        }
        if track_cols and "is_useful" not in track_cols:
            self.conn.execute(
                "ALTER TABLE tracking_intervals ADD COLUMN is_useful INTEGER"
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

    def get_tracking_useful_totals(self, d: date) -> tuple:
        row = self.conn.execute(
            """
            SELECT
                COALESCE(SUM(CASE WHEN ti.is_useful = 1 THEN ti.duration_secs END), 0) AS useful,
                COALESCE(SUM(CASE WHEN ti.is_useful = 0 THEN ti.duration_secs END), 0) AS not_useful
            FROM tracking_intervals ti
            JOIN tracking_sessions ts ON ts.id = ti.session_id
            WHERE ts.date = ? AND ti.ended_at IS NOT NULL
            """,
            (date_to_str(d),),
        ).fetchone()
        return int(row["useful"]), int(row["not_useful"])

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
        task_useful = int(row["useful"])
        task_not_useful = int(row["not_useful"])
        track_useful, track_not_useful = self.get_tracking_useful_totals(d)
        return task_useful + track_useful, task_not_useful + track_not_useful

    def get_day_activity_seconds(self, d: date) -> int:
        ds = date_to_str(d)
        task_row = self.conn.execute(
            "SELECT COALESCE(SUM(duration_seconds), 0) AS total FROM daily_tasks WHERE date = ?",
            (ds,),
        ).fetchone()
        track_row = self.conn.execute(
            """
            SELECT COALESCE(SUM(ti.duration_secs), 0) AS total
            FROM tracking_intervals ti
            JOIN tracking_sessions ts ON ts.id = ti.session_id
            WHERE ts.date = ? AND ti.ended_at IS NOT NULL
            """,
            (ds,),
        ).fetchone()
        return int(task_row["total"]) + int(track_row["total"])

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
        try:
            task_date = str_to_date(task.date)
        except ValueError:
            return
        tasks = self.get_tasks_for_date(task_date)
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
        try:
            d = str_to_date(task.date) + timedelta(days=1)
        except ValueError:
            return None
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
        row = self.conn.execute(
            "SELECT COALESCE(MAX(sort_order), -1) + 1 AS n FROM daily_tasks WHERE date = ?",
            (date_to_str(d),),
        ).fetchone()
        sort_order = int(row["n"])
        cursor = self.conn.execute(
            "INSERT INTO daily_tasks (date, title, recurring_id, sort_order) VALUES (?, ?, ?, ?)",
            (date_to_str(d), title, recurring_id, sort_order),
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
                SUM(useful) AS useful,
                SUM(not_useful) AS not_useful,
                SUM(total) AS total,
                SUM(task_count) AS task_count
            FROM (
                SELECT
                    date,
                    COALESCE(SUM(CASE WHEN is_useful = 1 THEN duration_seconds END), 0) AS useful,
                    COALESCE(SUM(CASE WHEN is_useful = 0 THEN duration_seconds END), 0) AS not_useful,
                    COALESCE(SUM(duration_seconds), 0) AS total,
                    COUNT(*) AS task_count
                FROM daily_tasks
                WHERE date >= ? AND date <= ?
                GROUP BY date
                UNION ALL
                SELECT
                    ts.date AS date,
                    COALESCE(SUM(CASE WHEN ti.is_useful = 1 THEN ti.duration_secs END), 0) AS useful,
                    COALESCE(SUM(CASE WHEN ti.is_useful = 0 THEN ti.duration_secs END), 0) AS not_useful,
                    COALESCE(SUM(ti.duration_secs), 0) AS total,
                    0 AS task_count
                FROM tracking_intervals ti
                JOIN tracking_sessions ts ON ts.id = ti.session_id
                WHERE ts.date >= ? AND ts.date <= ? AND ti.ended_at IS NOT NULL
                GROUP BY ts.date
            )
            GROUP BY date
            ORDER BY date
            """,
            (date_to_str(start), date_to_str(end), date_to_str(start), date_to_str(end)),
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

    def get_finance_entries_between(
        self, start: date, end: date
    ) -> List[FinanceEntry]:
        rows = self.conn.execute(
            """
            SELECT * FROM finance_entries
            WHERE date >= ? AND date <= ?
            ORDER BY date, id
            """,
            (start.isoformat(), end.isoformat()),
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

    def get_finance_monthly_totals_between(self, start: date, end: date) -> dict:
        rows = self.conn.execute(
            """
            SELECT category, entry_type, SUM(amount) AS total
            FROM finance_entries
            WHERE date >= ? AND date <= ?
            GROUP BY category, entry_type
            """,
            (start.isoformat(), end.isoformat()),
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

    def get_finance_daily_series_between(self, start: date, end: date) -> List[dict]:
        rows = self.conn.execute(
            """
            SELECT
                date,
                COALESCE(SUM(CASE WHEN entry_type = 'income' THEN amount END), 0) AS income,
                COALESCE(SUM(CASE WHEN entry_type = 'expense' THEN amount END), 0) AS expense,
                COALESCE(SUM(CASE WHEN entry_type = 'investment' THEN amount END), 0) AS investment
            FROM finance_entries
            WHERE date >= ? AND date <= ?
            GROUP BY date
            ORDER BY date
            """,
            (start.isoformat(), end.isoformat()),
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

    def get_backup_summary(self) -> dict:
        def _count(table: str) -> int:
            row = self.conn.execute(f"SELECT COUNT(*) AS c FROM {table}").fetchone()
            return int(row["c"])

        return {
            "tasks": _count("daily_tasks"),
            "finance": _count("finance_entries"),
            "wellness": _count("daily_wellness"),
            "notes": _count("daily_notes"),
            "recurring": _count("recurring_tasks"),
            "projects": _count("projects"),
            "project_tasks": _count("project_tasks"),
            "budget_limits": _count("budget_limits"),
            "important_dates": _count("important_dates"),
            "installments": _count("installments"),
            "installment_payments": _count("installment_payments"),
            "tracking_sessions": _count("tracking_sessions"),
            "tracking_intervals": _count("tracking_intervals"),
        }

    def export_json(self) -> dict:
        tasks = self.conn.execute("SELECT * FROM daily_tasks ORDER BY date, sort_order").fetchall()
        finance = self.conn.execute("SELECT * FROM finance_entries ORDER BY date").fetchall()
        wellness = self.conn.execute("SELECT * FROM daily_wellness ORDER BY date").fetchall()
        notes = self.conn.execute("SELECT * FROM daily_notes ORDER BY date").fetchall()
        recurring = self.conn.execute("SELECT * FROM recurring_tasks ORDER BY id").fetchall()
        settings_rows = self.conn.execute("SELECT * FROM settings").fetchall()
        projects = self.conn.execute("SELECT * FROM projects ORDER BY id").fetchall()
        proj_tasks = self.conn.execute(
            "SELECT * FROM project_tasks ORDER BY project_id, sort_order"
        ).fetchall()
        budgets = self.conn.execute("SELECT * FROM budget_limits").fetchall()
        important_dates = self.conn.execute(
            "SELECT * FROM important_dates ORDER BY date"
        ).fetchall()
        installments = self.conn.execute(
            "SELECT * FROM installments ORDER BY id"
        ).fetchall()
        inst_payments = self.conn.execute(
            "SELECT * FROM installment_payments ORDER BY installment_id, payment_date"
        ).fetchall()
        tracking_sessions = self.conn.execute(
            "SELECT * FROM tracking_sessions ORDER BY date, id"
        ).fetchall()
        tracking_intervals = self.conn.execute(
            "SELECT * FROM tracking_intervals ORDER BY session_id, started_at"
        ).fetchall()
        skip_settings = {"active_timer_task_id", "active_timer_started_at"}
        settings = {
            r["key"]: r["value"]
            for r in settings_rows
            if r["key"] not in skip_settings
        }
        return {
            "version": 2,
            "tasks": [dict(r) for r in tasks],
            "finance": [dict(r) for r in finance],
            "wellness": [dict(r) for r in wellness],
            "notes": [dict(r) for r in notes],
            "recurring": [dict(r) for r in recurring],
            "settings": settings,
            "projects": [dict(r) for r in projects],
            "project_tasks": [dict(r) for r in proj_tasks],
            "budget_limits": [dict(r) for r in budgets],
            "important_dates": [dict(r) for r in important_dates],
            "installments": [dict(r) for r in installments],
            "installment_payments": [dict(r) for r in inst_payments],
            "tracking_sessions": [dict(r) for r in tracking_sessions],
            "tracking_intervals": [dict(r) for r in tracking_intervals],
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
            if f.get("entry_type") not in ("income", "expense", "investment"):
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

        settings = data.get("settings")
        if settings is not None and not isinstance(settings, dict):
            return False, "تنظیمات خراب هستند"

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

            installments = data.get("installments")
            if installments is not None:
                if not isinstance(installments, list):
                    return False, "اقساط خراب هستند"
                for inst in installments:
                    if not isinstance(inst, dict):
                        return False, "اقساط خراب هستند"
                    if not isinstance(inst.get("title"), str):
                        return False, "اقساط خراب هستند"
                    if "id" not in inst or "start_date" not in inst:
                        return False, "اقساط خراب هستند"
                    try:
                        if int(inst.get("amount", 0)) <= 0:
                            return False, "اقساط خراب هستند"
                        total_count = int(inst.get("total_count", 0))
                        paid_count = int(inst.get("paid_count", 0))
                        if total_count <= 0:
                            return False, "اقساط خراب هستند"
                        if paid_count > total_count:
                            return False, "اقساط خراب هستند"
                    except (TypeError, ValueError):
                        return False, "اقساط خراب هستند"

            inst_payments = data.get("installment_payments")
            if inst_payments is not None:
                if not isinstance(inst_payments, list):
                    return False, "اقساط خراب هستند"
                for pay in inst_payments:
                    if not isinstance(pay, dict):
                        return False, "اقساط خراب هستند"
                    if "id" not in pay or "installment_id" not in pay or "payment_date" not in pay:
                        return False, "اقساط خراب هستند"

            important_dates = data.get("important_dates")
            if important_dates is not None:
                if not isinstance(important_dates, list):
                    return False, "تاریخ‌های مهم خراب هستند"
                for item in important_dates:
                    if not isinstance(item, dict):
                        return False, "تاریخ‌های مهم خراب هستند"
                    if not isinstance(item.get("title"), str) or not isinstance(item.get("date"), str):
                        return False, "تاریخ‌های مهم خراب هستند"
                    if "id" not in item:
                        return False, "تاریخ‌های مهم خراب هستند"

            budget_limits = data.get("budget_limits")
            if budget_limits is not None:
                if not isinstance(budget_limits, list):
                    return False, "بودجه‌ها خراب هستند"
                for b in budget_limits:
                    if not isinstance(b, dict) or not isinstance(b.get("category"), str):
                        return False, "بودجه‌ها خراب هستند"

        for t in tasks:
            try:
                date.fromisoformat(t["date"])
            except ValueError:
                return False, "تسک‌ها خراب هستند"

        for f in finance:
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
            self.conn.execute("DELETE FROM important_dates")
            self.conn.execute("DELETE FROM installment_payments")
            self.conn.execute("DELETE FROM installments")
            self.conn.execute("DELETE FROM tracking_intervals")
            self.conn.execute("DELETE FROM tracking_sessions")
            self.conn.execute("DELETE FROM settings")

            try:
                for tbl in (
                    "daily_tasks",
                    "finance_entries",
                    "recurring_tasks",
                    "projects",
                    "project_tasks",
                    "important_dates",
                    "installments",
                    "installment_payments",
                    "tracking_sessions",
                    "tracking_intervals",
                ):
                    self.conn.execute(
                        "DELETE FROM sqlite_sequence WHERE name = ?", (tbl,)
                    )
            except Exception as _seq_err:
                print(f"[import warning] sqlite_sequence reset failed: {_seq_err}")

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

            for d in data.get("important_dates", []):
                self.conn.execute(
                    "INSERT INTO important_dates"
                    " (id, title, date, category, notes, repeat_type, repeat_months, created_at)"
                    " VALUES (?,?,?,?,?,?,?,?)",
                    (
                        d["id"],
                        d["title"],
                        d["date"],
                        d.get("category", "سایر"),
                        d.get("notes", ""),
                        d.get("repeat_type", "none"),
                        int(d.get("repeat_months", 0)),
                        d.get("created_at", ""),
                    ),
                )

            for inst in data.get("installments", []):
                self.conn.execute(
                    "INSERT INTO installments"
                    " (id, title, amount, total_count, paid_count, start_date, due_day, created_at)"
                    " VALUES (?,?,?,?,?,?,?,?)",
                    (
                        inst.get("id"),
                        inst.get("title", ""),
                        int(inst.get("amount", 0)),
                        int(inst.get("total_count", 1)),
                        int(inst.get("paid_count", 0)),
                        inst.get("start_date", ""),
                        int(inst.get("due_day", 1)),
                        inst.get("created_at", ""),
                    ),
                )

            for pay in data.get("installment_payments", []):
                self.conn.execute(
                    "INSERT INTO installment_payments (id, installment_id, payment_date, created_at)"
                    " VALUES (?,?,?,?)",
                    (
                        pay.get("id"),
                        pay.get("installment_id"),
                        pay.get("payment_date", ""),
                        pay.get("created_at", ""),
                    ),
                )

            for ts in data.get("tracking_sessions", []):
                self.conn.execute(
                    "INSERT INTO tracking_sessions (id, date, started_at, ended_at, created_at)"
                    " VALUES (?,?,?,?,?)",
                    (
                        ts.get("id"),
                        ts.get("date", ""),
                        ts.get("started_at"),
                        ts.get("ended_at"),
                        ts.get("created_at", ""),
                    ),
                )

            for ti in data.get("tracking_intervals", []):
                self.conn.execute(
                    "INSERT INTO tracking_intervals"
                    " (id, session_id, started_at, ended_at, label, duration_secs, is_useful)"
                    " VALUES (?,?,?,?,?,?,?)",
                    (
                        ti.get("id"),
                        ti.get("session_id"),
                        ti.get("started_at"),
                        ti.get("ended_at"),
                        ti.get("label", ""),
                        ti.get("duration_secs"),
                        ti.get("is_useful"),
                    ),
                )

            _skip_import_keys = {"active_timer_task_id", "active_timer_started_at"}
            settings = data.get("settings")
            if isinstance(settings, dict):
                for key, value in settings.items():
                    if key in _skip_import_keys:
                        continue
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

    def pay_installment(
        self, inst_id: int, payment_date: Optional[date] = None
    ) -> Optional[Installment]:
        """Record one payment. Returns updated installment or None if already settled."""
        inst = self.get_installment_by_id(inst_id)
        if inst is None or inst.is_settled:
            return None
        now_str = datetime.now().isoformat()
        pay_str = date_to_str(payment_date or date.today())
        self.conn.execute(
            "UPDATE installments SET paid_count = paid_count + 1 WHERE id = ?",
            (inst_id,),
        )
        self.conn.execute(
            "INSERT INTO installment_payments (installment_id, payment_date, created_at)"
            " VALUES (?,?,?)",
            (inst_id, pay_str, now_str),
        )
        self.conn.commit()
        return self.get_installment_by_id(inst_id)

    def pay_installment_and_record(
        self,
        inst_id: int,
        payment_date: date,
        amount: int,
        finance_title: str,
        category: str = "اقساط",
    ) -> Optional[Installment]:
        """Atomically record installment payment and matching finance expense."""
        inst = self.get_installment_by_id(inst_id)
        if inst is None or inst.is_settled:
            return None
        now_str = datetime.now().isoformat()
        pay_str = date_to_str(payment_date)
        with self.conn:
            self.conn.execute(
                "UPDATE installments SET paid_count = paid_count + 1 WHERE id = ?",
                (inst_id,),
            )
            self.conn.execute(
                "INSERT INTO installment_payments (installment_id, payment_date, created_at)"
                " VALUES (?,?,?)",
                (inst_id, pay_str, now_str),
            )
            self.conn.execute(
                """
                INSERT INTO finance_entries (date, entry_type, title, amount, category)
                VALUES (?, 'expense', ?, ?, ?)
                """,
                (pay_str, finance_title, amount, category),
            )
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

    def is_paid_in_date_range(self, inst_id: int, start: date, end: date) -> bool:
        row = self.conn.execute(
            "SELECT 1 FROM installment_payments"
            " WHERE installment_id=? AND payment_date >= ? AND payment_date <= ?",
            (inst_id, start.isoformat(), end.isoformat()),
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

    def get_installments_summary_for_range(self, start: date, end: date) -> dict:
        """Active installments with payment status for a Gregorian date range."""
        installments = self.get_all_installments()
        active = [i for i in installments if not i.is_settled]
        result = []
        for inst in active:
            paid_month = self.is_paid_in_date_range(inst.id, start, end)
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

    # ── important dates ─────────────────────────────────────────────────────

    def get_all_important_dates(self) -> List[ImportantDate]:
        rows = self.conn.execute(
            "SELECT * FROM important_dates ORDER BY date ASC"
        ).fetchall()
        return [ImportantDate.from_row(r) for r in rows]

    def get_important_date_by_id(self, date_id: int) -> Optional[ImportantDate]:
        row = self.conn.execute(
            "SELECT * FROM important_dates WHERE id = ?", (date_id,)
        ).fetchone()
        return ImportantDate.from_row(row) if row else None

    def add_important_date(
        self, title: str, date_str: str, category: str,
        notes: str, repeat_type: str, repeat_months: int
    ) -> ImportantDate:
        now = datetime.now().isoformat()
        cursor = self.conn.execute(
            "INSERT INTO important_dates"
            " (title, date, category, notes, repeat_type, repeat_months, created_at)"
            " VALUES (?,?,?,?,?,?,?)",
            (title.strip(), date_str, category, notes.strip(),
             repeat_type, repeat_months, now)
        )
        self.conn.commit()
        return self.get_important_date_by_id(cursor.lastrowid)

    def edit_important_date(
        self, date_id: int, title: str, date_str: str, category: str,
        notes: str, repeat_type: str, repeat_months: int
    ):
        self.conn.execute(
            "UPDATE important_dates"
            " SET title=?, date=?, category=?, notes=?,"
            "     repeat_type=?, repeat_months=?"
            " WHERE id=?",
            (title.strip(), date_str, category, notes.strip(),
             repeat_type, repeat_months, date_id)
        )
        self.conn.commit()

    def delete_important_date(self, date_id: int):
        self.conn.execute("DELETE FROM important_dates WHERE id=?", (date_id,))
        self.conn.commit()

    def renew_important_date(self, date_id: int) -> Optional[ImportantDate]:
        """Advance date by repeat period. For 'none', do nothing."""
        import calendar
        item = self.get_important_date_by_id(date_id)
        if item is None or item.repeat_type == "none":
            return item
        months = 12 if item.repeat_type == "yearly" else item.repeat_months
        if months <= 0:
            return item
        try:
            d = date.fromisoformat(item.date)
        except ValueError:
            return item
        total_months = d.month - 1 + months
        new_year = d.year + total_months // 12
        new_month = total_months % 12 + 1
        last_day = calendar.monthrange(new_year, new_month)[1]
        new_day = min(d.day, last_day)
        new_date = date(new_year, new_month, new_day).isoformat()
        self.conn.execute(
            "UPDATE important_dates SET date=? WHERE id=?",
            (new_date, date_id)
        )
        self.conn.commit()
        return self.get_important_date_by_id(date_id)

    def count_urgent_dates(self, today: date, threshold_days: int = 7) -> int:
        """Count upcoming dates within threshold and recently overdue ones."""
        today_str = date_to_str(today)
        future_cutoff = date_to_str(today + timedelta(days=threshold_days))
        past_cutoff = date_to_str(today - timedelta(days=threshold_days))
        row = self.conn.execute(
            """
            SELECT COUNT(*) AS c FROM important_dates
            WHERE (date >= ? AND date <= ?)
               OR (date < ? AND date >= ?)
            """,
            (today_str, future_cutoff, today_str, past_cutoff),
        ).fetchone()
        return int(row["c"])

    # ── tracking ──────────────────────────────────────────────────────────────

    def start_tracking_session(self, d: date) -> int:
        """Create a new session and its first interval. Returns session id."""
        self.close_stale_tracking_sessions(d)
        active = self.get_active_tracking_session(d)
        if active:
            return active["id"]
        now_epoch = time.time()
        now_str = datetime.now().isoformat()
        cur = self.conn.execute(
            "INSERT INTO tracking_sessions (date, started_at, created_at) VALUES (?,?,?)",
            (date_to_str(d), now_epoch, now_str),
        )
        session_id = cur.lastrowid
        self.conn.execute(
            "INSERT INTO tracking_intervals (session_id, started_at) VALUES (?,?)",
            (session_id, now_epoch),
        )
        self.conn.commit()
        return session_id

    def close_stale_tracking_sessions(self, today: date) -> None:
        """Auto-stop tracking sessions left active from previous days."""
        today_str = date_to_str(today)
        rows = self.conn.execute(
            "SELECT id FROM tracking_sessions WHERE date < ? AND ended_at IS NULL",
            (today_str,),
        ).fetchall()
        for row in rows:
            self.stop_tracking(row["id"])

    def get_tracking_session_by_id(self, session_id: int):
        return self.conn.execute(
            "SELECT * FROM tracking_sessions WHERE id=?",
            (session_id,),
        ).fetchone()

    def switch_tracking(self, session_id: int) -> bool:
        """Close active interval and open a new one."""
        row = self.get_tracking_session_by_id(session_id)
        if not row or row["ended_at"] is not None:
            return False
        now_epoch = time.time()
        active = self.conn.execute(
            "SELECT id, started_at FROM tracking_intervals WHERE session_id=? AND ended_at IS NULL",
            (session_id,),
        ).fetchone()
        if active:
            duration = int(now_epoch - active["started_at"])
            self.conn.execute(
                "UPDATE tracking_intervals SET ended_at=?, duration_secs=? WHERE id=?",
                (now_epoch, duration, active["id"]),
            )
        self.conn.execute(
            "INSERT INTO tracking_intervals (session_id, started_at) VALUES (?,?)",
            (session_id, now_epoch),
        )
        self.conn.commit()
        return True

    def stop_tracking(self, session_id: int) -> bool:
        """Close active interval and close the session."""
        row = self.get_tracking_session_by_id(session_id)
        if not row or row["ended_at"] is not None:
            return False
        now_epoch = time.time()
        active = self.conn.execute(
            "SELECT id, started_at FROM tracking_intervals WHERE session_id=? AND ended_at IS NULL",
            (session_id,),
        ).fetchone()
        if active:
            duration = int(now_epoch - active["started_at"])
            self.conn.execute(
                "UPDATE tracking_intervals SET ended_at=?, duration_secs=? WHERE id=?",
                (now_epoch, duration, active["id"]),
            )
        self.conn.execute(
            "UPDATE tracking_sessions SET ended_at=? WHERE id=?",
            (now_epoch, session_id),
        )
        self.conn.commit()
        return True

    def set_tracking_label(self, interval_id: int, label: str) -> None:
        self.conn.execute(
            "UPDATE tracking_intervals SET label=? WHERE id=?",
            (label.strip(), interval_id),
        )
        self.conn.commit()

    def set_tracking_useful(self, interval_id: int, is_useful: Optional[bool]) -> None:
        value = None
        if is_useful is not None:
            value = 1 if is_useful else 0
        self.conn.execute(
            "UPDATE tracking_intervals SET is_useful=? WHERE id=?",
            (value, interval_id),
        )
        self.conn.commit()

    def get_active_tracking_session(self, d: date):
        """Returns the active (not ended) session row for given date, or None."""
        return self.conn.execute(
            "SELECT * FROM tracking_sessions WHERE date=? AND ended_at IS NULL ORDER BY id DESC LIMIT 1",
            (date_to_str(d),),
        ).fetchone()

    def get_tracking_sessions_for_date(self, d: date):
        return self.conn.execute(
            "SELECT * FROM tracking_sessions WHERE date=? ORDER BY started_at ASC",
            (date_to_str(d),),
        ).fetchall()

    def get_last_tracking_session(self, d: date):
        """Returns the most recent session for given date (active or ended)."""
        return self.conn.execute(
            "SELECT * FROM tracking_sessions WHERE date=? ORDER BY id DESC LIMIT 1",
            (date_to_str(d),),
        ).fetchone()

    def get_tracking_intervals(self, session_id: int):
        return self.conn.execute(
            "SELECT * FROM tracking_intervals WHERE session_id=? ORDER BY started_at ASC",
            (session_id,),
        ).fetchall()

    def get_tracking_interval(self, interval_id: int):
        return self.conn.execute(
            "SELECT * FROM tracking_intervals WHERE id=?",
            (interval_id,),
        ).fetchone()

    def delete_tracking_interval(self, interval_id: int) -> bool:
        """Delete a completed interval. Returns False if active or missing."""
        row = self.get_tracking_interval(interval_id)
        if not row or row["ended_at"] is None:
            return False
        session_id = row["session_id"]
        self.conn.execute("DELETE FROM tracking_intervals WHERE id=?", (interval_id,))
        remaining = self.conn.execute(
            "SELECT COUNT(*) AS c FROM tracking_intervals WHERE session_id=?",
            (session_id,),
        ).fetchone()["c"]
        if remaining == 0:
            self.conn.execute("DELETE FROM tracking_sessions WHERE id=?", (session_id,))
        self.conn.commit()
        return True

    def delete_tracking_session(self, session_id: int) -> bool:
        row = self.conn.execute(
            "SELECT id FROM tracking_sessions WHERE id=?",
            (session_id,),
        ).fetchone()
        if not row:
            return False
        self.conn.execute(
            "DELETE FROM tracking_intervals WHERE session_id=?",
            (session_id,),
        )
        self.conn.execute("DELETE FROM tracking_sessions WHERE id=?", (session_id,))
        self.conn.commit()
        return True
