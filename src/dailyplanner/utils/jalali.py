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


def jalali_month_last_day(jy: int, jm: int) -> int:
    if jm == 12:
        return 30 if jdatetime.date.isleap(jy) else 29
    return jdatetime.j_days_in_month[jm - 1]


def jalali_month_bounds(jy: int, jm: int) -> tuple:
    """Gregorian start/end dates (inclusive) for a Jalali month."""
    start = jalali_to_gregorian(jy, jm, 1)
    end = jalali_to_gregorian(jy, jm, jalali_month_last_day(jy, jm))
    return start, end


def prev_jalali_month(jy: int, jm: int) -> tuple:
    if jm == 1:
        return jy - 1, 12
    return jy, jm - 1


def next_jalali_month(jy: int, jm: int) -> tuple:
    if jm == 12:
        return jy + 1, 1
    return jy, jm + 1


def current_jalali_ym(d: date = None) -> tuple:
    d = d or date.today()
    return gregorian_to_jalali_parts(d)[:2]
