from __future__ import annotations

from dataclasses import dataclass, asdict, field
from datetime import date
from decimal import Decimal
from typing import Any, Dict, Optional

from pftracker.utils import to_date, to_decimal


# ----------------------------- Exceptions ---------------------------------
class FinanceError(Exception):
    pass


class UnknownCategory(FinanceError):
    pass


class UnknownTransaction(FinanceError):
    pass


class BudgetError(FinanceError):
    pass


class ExchangeRateError(FinanceError):
    pass


# ---------------------------- Data models ---------------------------------
@dataclass
class Transaction:
    id: str
    date: date
    category: Optional[str]
    currency: str
    amount: Decimal  # positive for income, negative for expense
    description: str = ""
    meta: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["date"] = self.date.isoformat()
        d["amount"] = str(self.amount)
        return d

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Transaction":
        return Transaction(
            id=d["id"],
            date=to_date(d["date"]),
            category=d.get("category"),
            currency=d["currency"],
            amount=to_decimal(d["amount"]),
            description=d.get("description", ""),
            meta=d.get("meta", {}),
        )
