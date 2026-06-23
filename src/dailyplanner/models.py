import calendar
from dataclasses import dataclass
from datetime import date
from typing import Literal, Optional

FinanceType = Literal["income", "expense", "investment"]


@dataclass
class RecurringTask:
    id: int
    title: str
    created_at: str


@dataclass
class DailyTask:
    id: int
    date: str
    title: str
    duration_seconds: int
    estimated_seconds: int
    is_useful: Optional[bool]
    recurring_id: Optional[int]
    sort_order: int = 0

    @property
    def is_starred(self) -> bool:
        return self.recurring_id is not None

    def remaining_seconds(self, spent_seconds: Optional[int] = None) -> Optional[int]:
        if self.estimated_seconds <= 0:
            return None
        spent = self.duration_seconds if spent_seconds is None else spent_seconds
        return max(0, self.estimated_seconds - spent)

    @classmethod
    def from_row(cls, row) -> "DailyTask":
        is_useful = None
        if row["is_useful"] is not None:
            is_useful = bool(row["is_useful"])
        keys = row.keys()
        estimated = row["estimated_seconds"] if "estimated_seconds" in keys else 0
        sort_order = row["sort_order"] if "sort_order" in keys else 0
        return cls(
            id=row["id"],
            date=row["date"],
            title=row["title"],
            duration_seconds=row["duration_seconds"],
            estimated_seconds=estimated,
            is_useful=is_useful,
            recurring_id=row["recurring_id"],
            sort_order=sort_order,
        )


from dailyplanner.utils.jalali import to_persian_digits


def format_duration(seconds: int) -> str:
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    text = f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return to_persian_digits(text)


def format_duration_or_dash(seconds: Optional[int]) -> str:
    if seconds is None:
        return to_persian_digits("—")
    return format_duration(seconds)


def date_to_str(d: date) -> str:
    return d.isoformat()


def str_to_date(s: str) -> date:
    return date.fromisoformat(s)


@dataclass
class FinanceEntry:
    id: int
    date: str
    entry_type: FinanceType
    title: str
    amount: int
    category: str = "عمومی"

    @property
    def is_income(self) -> bool:
        return self.entry_type == "income"

    @property
    def is_investment(self) -> bool:
        return self.entry_type == "investment"

    @classmethod
    def from_row(cls, row) -> "FinanceEntry":
        keys = row.keys()
        category = row["category"] if "category" in keys else "عمومی"
        return cls(
            id=row["id"],
            date=row["date"],
            entry_type=row["entry_type"],
            title=row["title"],
            amount=row["amount"],
            category=category or "عمومی",
        )


@dataclass
class DailyWellness:
    date: str
    sleep_minutes: Optional[int]
    wake_minutes: Optional[int]
    mood_score: Optional[int]

    @classmethod
    def from_row(cls, row) -> "DailyWellness":
        return cls(
            date=row["date"],
            sleep_minutes=row["sleep_minutes"],
            wake_minutes=row["wake_minutes"],
            mood_score=row["mood_score"],
        )

    def sleep_duration_minutes(self) -> Optional[int]:
        if self.sleep_minutes is None or self.wake_minutes is None:
            return None
        if self.sleep_minutes > self.wake_minutes:
            return (24 * 60 - self.sleep_minutes) + self.wake_minutes
        return self.wake_minutes - self.sleep_minutes


def format_clock_time(minutes: Optional[int]) -> str:
    if minutes is None:
        return to_persian_digits("—")
    hours = minutes // 60
    mins = minutes % 60
    return to_persian_digits(f"{hours:02d}:{mins:02d}")


def format_sleep_duration(minutes: Optional[int]) -> str:
    if minutes is None:
        return to_persian_digits("—")
    hours = minutes // 60
    mins = minutes % 60
    if hours and mins:
        return to_persian_digits(f"{hours} ساعت و {mins} دقیقه")
    if hours:
        return to_persian_digits(f"{hours} ساعت")
    return to_persian_digits(f"{mins} دقیقه")


def format_money(amount: int) -> str:
    sign = "−" if amount < 0 else ""
    text = f"{sign}{abs(amount):,}".replace(",", "،")
    return to_persian_digits(text)


@dataclass
class Project:
    id: int
    title: str
    color: str
    deadline: Optional[str]
    is_done: bool
    created_at: str

    @classmethod
    def from_row(cls, row) -> "Project":
        return cls(
            id=row["id"],
            title=row["title"],
            color=row["color"],
            deadline=row["deadline"],
            is_done=bool(row["is_done"]),
            created_at=row["created_at"],
        )

    def days_until_deadline(self) -> Optional[int]:
        if not self.deadline:
            return None
        try:
            delta = date.fromisoformat(self.deadline) - date.today()
            return delta.days
        except ValueError:
            return None


@dataclass
class Installment:
    id: int
    title: str
    amount: int
    total_count: int
    paid_count: int
    start_date: str
    due_day: int
    created_at: str

    @classmethod
    def from_row(cls, row) -> "Installment":
        return cls(
            id=row["id"],
            title=row["title"],
            amount=row["amount"],
            total_count=row["total_count"],
            paid_count=row["paid_count"],
            start_date=row["start_date"],
            due_day=row["due_day"],
            created_at=row["created_at"],
        )

    @property
    def is_settled(self) -> bool:
        return self.paid_count >= self.total_count

    @property
    def remaining_count(self) -> int:
        return max(0, self.total_count - self.paid_count)

    @property
    def remaining_amount(self) -> int:
        return self.remaining_count * self.amount

    def next_due_date(self) -> Optional[date]:
        """Gregorian date of next unpaid installment's due date."""
        if self.is_settled:
            return None
        try:
            base = date.fromisoformat(self.start_date)
        except ValueError:
            return None
        month = base.month - 1 + self.paid_count
        year = base.year + month // 12
        month = month % 12 + 1
        last_day = calendar.monthrange(year, month)[1]
        day = min(self.due_day, last_day)
        return date(year, month, day)


@dataclass
class ImportantDate:
    id: int
    title: str
    date: str
    category: str
    notes: str
    repeat_type: str
    repeat_months: int
    created_at: str

    @classmethod
    def from_row(cls, row) -> "ImportantDate":
        return cls(
            id=row["id"],
            title=row["title"],
            date=row["date"],
            category=row["category"],
            notes=row["notes"],
            repeat_type=row["repeat_type"],
            repeat_months=row["repeat_months"],
            created_at=row["created_at"],
        )

    def days_until(self, today: date = None) -> int:
        if today is None:
            today = date.today()
        try:
            return (date.fromisoformat(self.date) - today).days
        except ValueError:
            return 0

    @property
    def is_repeating(self) -> bool:
        return self.repeat_type != "none"


@dataclass
class ProjectTask:
    id: int
    project_id: int
    title: str
    is_done: bool
    sort_order: int
    created_at: str

    @classmethod
    def from_row(cls, row) -> "ProjectTask":
        return cls(
            id=row["id"],
            project_id=row["project_id"],
            title=row["title"],
            is_done=bool(row["is_done"]),
            sort_order=row["sort_order"],
            created_at=row["created_at"],
        )
