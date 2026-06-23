"""Parse bank SMS text to extract transaction amounts."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal, Optional

_PERSIAN_DIGITS = "\u06f0\u06f1\u06f2\u06f3\u06f4\u06f5\u06f6\u06f7\u06f8\u06f9"
_ARABIC_DIGITS = "\u0660\u0661\u0662\u0663\u0664\u0665\u0666\u0667\u0668\u0669"
_ASCII_DIGITS = "0123456789"
_DIGIT_MAP = str.maketrans(
    {**dict(zip(_PERSIAN_DIGITS, _ASCII_DIGITS)), **dict(zip(_ARABIC_DIGITS, _ASCII_DIGITS))}
)

_RIAL_TO_TOMAN = 10
_AMOUNT_LINE = re.compile(r"^([+-])\s*([\d,\u060c]+)$")


@dataclass(frozen=True)
class ParsedBankSms:
    amount: int = 0
    direction: Optional[Literal["income", "expense"]] = None


def normalize_digits(text) -> str:
    if text is None:
        return ""
    return str(text).translate(_DIGIT_MAP)


def _strip_group_separators(text: str) -> str:
    return text.replace(",", "").replace("\u060c", "")


def _parse_int(raw: str) -> Optional[int]:
    cleaned = _strip_group_separators(normalize_digits(raw)).strip()
    if not cleaned or not cleaned.lstrip("+-").isdigit():
        return None
    return abs(int(cleaned))


def _rial_to_toman(rial: int) -> int:
    return rial // _RIAL_TO_TOMAN


def parse_bank_sms(text: str) -> ParsedBankSms:
    if not text or not text.strip():
        return ParsedBankSms()

    normalized = text.translate(_DIGIT_MAP).strip()
    amount = 0
    direction: Optional[Literal["income", "expense"]] = None

    for line in normalized.splitlines():
        match = _AMOUNT_LINE.match(line.strip())
        if not match:
            continue
        parsed = _parse_int(match.group(2))
        if parsed and parsed > 0:
            amount = _rial_to_toman(parsed)
            direction = "income" if match.group(1) == "+" else "expense"
            break

    return ParsedBankSms(amount=amount, direction=direction)


def resolve_amount(amount_raw, sms_text: str = "") -> int:
    cleaned = _strip_group_separators(normalize_digits(amount_raw)).strip()
    try:
        amount = int(float(cleaned or 0))
    except (TypeError, ValueError):
        amount = 0
    if amount > 0:
        return amount
    parsed = parse_bank_sms(str(sms_text or ""))
    return parsed.amount
