from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation, getcontext
from typing import Any

# Set safe decimal precision for money math
getcontext().prec = 28


def to_date(value: Any) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return datetime.strptime(value.replace("/", "-"), "%Y-%m-%d").date()
        except ValueError as e:
            raise ValueError(f"Invalid date string: {value!r}") from e
    raise TypeError(f"Unsupported date type: {type(value)}")


def to_decimal(value: Any) -> Decimal:
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError) as e:
        raise ValueError(f"Invalid decimal value: {value!r}") from e


def month_key(d: date) -> str:
    return f"{d.year:04d}-{d.month:02d}"


def quantize(amount: Decimal, currency: str) -> Decimal:
    places = Decimal("0.01") if currency.upper() != "JPY" else Decimal("1")
    return amount.quantize(places, rounding=ROUND_HALF_UP)
