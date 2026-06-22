from datetime import date, timedelta

import jdatetime

PERSIAN_DIGITS = "۰۱۲۳۴۵۶۷۸۹"
MONTH_NAMES = [
    "",
    "فروردین",
    "اردیبهشت",
    "خرداد",
    "تیر",
    "مرداد",
    "شهریور",
    "مهر",
    "آبان",
    "آذر",
    "دی",
    "بهمن",
    "اسفند",
]


def to_persian_digits(value) -> str:
    text = str(value)
    return "".join(PERSIAN_DIGITS[int(ch)] if ch.isdigit() else ch for ch in text)


def format_jalali(d: date) -> str:
    jd = jdatetime.date.fromgregorian(date=d)
    weekday = jd.j_weekdays_fa[jd.weekday()]
    month = MONTH_NAMES[jd.month]
    day = to_persian_digits(jd.day)
    year = to_persian_digits(jd.year)
    return f"{weekday}، {day} {month} {year}"


def add_days(d: date, days: int) -> date:
    return d + timedelta(days=days)


def gregorian_to_jalali_parts(d: date) -> tuple:
    jd = jdatetime.date.fromgregorian(date=d)
    return jd.year, jd.month, jd.day


def jalali_to_gregorian(year: int, month: int, day: int) -> date:
    jd = jdatetime.date(year, month, day)
    return jd.togregorian()
