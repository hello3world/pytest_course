from __future__ import annotations

import logging
import os
import uuid
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from pftracker.fx import ExchangeRateProvider, ECBRateProvider
from pftracker.models import Transaction, UnknownCategory, UnknownTransaction
from pftracker.storage import StorageBackend, JsonFileStorage
from pftracker.utils import to_date, to_decimal, quantize

logger = logging.getLogger("pftracker")


class PersonalFinanceTracker:
    """Single-wallet personal finance API with durable storage.

    The base currency decides how balances and budgets are presented.
    Transactions may be recorded in any currency; conversions use the injected
    ExchangeRateProvider.

    Important:
        The tracker must be **closed** after use to ensure storage is saved and
        the backend is released correctly. This can be done explicitly by calling
        :meth:`close`, or implicitly by using a ``with`` statement (recommended).

    Examples:
        Quick start (manual close):

        >>> from pftracker import PersonalFinanceTracker
        >>> t = PersonalFinanceTracker(base_currency="EUR")
        >>> t.add_category("Groceries")
        >>> t.add_transaction("2025-08-01", Decimal("-42.50"), category="Groceries", currency="EUR", description="Supermarkt")
        >>> t.balance()
        Decimal('...')
        >>> t.close()  # ensure results are saved and storage is released

        Using as a context manager (auto-close on exit):

        >>> from pftracker import PersonalFinanceTracker
        >>> with PersonalFinanceTracker() as t:
        ...     t.add_category("Salary")
        ...     t.add_transaction("2025-08-01", 3500, category="Salary", currency="EUR")
        ...     _ = t.balance()  # Decimal('...')
    """

    DEFAULT_PATH: Path = Path.home() / ".cache" / "pftracker" / "finance.json"

    def __init__(
            self,
            storage: Optional[StorageBackend] = None,
            base_currency: str = None,
            exchange_provider: Optional[ExchangeRateProvider] = None,
    ) -> None:
        """Create a new tracker instance with optional custom storage and FX provider.

        If `base_currency` is not provided, the environment variable ``DEFAULT_CURRENCY``
        is used, defaulting to ``"EUR"``. By default, data is persisted to
        ``~/.cache/pftracker/finance.json`` and exchange rates are fetched via
        :class:`pftracker.fx.ECBRateProvider`.

        Args:
            storage: Custom storage backend. Defaults to :class:`pftracker.storage.JsonFileStorage`.
            base_currency: ISO currency code (e.g. "EUR", "USD") for reporting.
            exchange_provider: Exchange rate provider used for currency conversions.
        """
        if base_currency is None:
            base_currency = os.environ.get("DEFAULT_CURRENCY", "EUR")
        self.base_currency = base_currency.upper()
        self.exchange = exchange_provider or ECBRateProvider()

        self.storage = storage or JsonFileStorage(self.DEFAULT_PATH)
        self.storage.reserve(self)

        # State
        self._transactions: List[Transaction] = []
        self._budgets: Dict[Tuple[str, str], Decimal] = {}
        self._categories: set[str] = set()
        self._closed = False

        # Try loading previous state
        data = self.storage.load() or {}
        if data:
            logger.info("Loading previous state from storage backend")
            self._load_from_dict(data)

    # --------------------------- Categories --------------------------------
    def add_category(self, name: str) -> None:
        """Create a new spending/earning category.

        Whitespace is trimmed; empty names are rejected.

        Args:
            name: Category name (e.g. ``"Groceries"``).

        Raises:
            ValueError: If the name is empty after trimming.

        Examples:
            >>> t = PersonalFinanceTracker()
            >>> t.add_category("Groceries")
            >>> t.list_categories()
            ['Groceries']
        """
        self._ensure_open()

        name = name.strip()
        if not name:
            raise ValueError("Category name cannot be empty")
        self._categories.add(name)
        logger.info("Added category '%s'", name)

    def delete_category(self, name: str) -> None:
        """Remove an existing category.

        Args:
            name: Name of the category to remove.

        Raises:
            UnknownCategory: If the category doesn't exist.

        Examples:
            >>> t = PersonalFinanceTracker()
            >>> t.add_category("Subscriptions")
            >>> t.delete_category("Subscriptions")
            >>> t.list_categories()
            []
        """
        self._ensure_open()

        if name not in self._categories:
            raise UnknownCategory(name)
        self._categories.remove(name)
        logger.info("Deleted category '%s'", name)

    def list_categories(self) -> List[str]:
        """List all known categories, sorted alphabetically.

        Returns:
            A list of category names.

        Examples:
            >>> t = PersonalFinanceTracker()
            >>> t.add_category("A")
            >>> t.add_category("B")
            >>> t.list_categories()
            ['A', 'B']
        """
        self._ensure_open()

        return sorted(self._categories)

    # ------------------------- Transactions --------------------------------
    def add_transaction(
            self,
            when: Any,
            amount: Any,
            *,
            currency: str = None,
            category: Optional[str] = None,
            description: str = "",
            meta: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Record a new transaction (expense is negative, income is positive).

        If `currency` is omitted, the tracker’s `base_currency` is used.
        Amount is quantized according to the transaction currency’s precision.

        Args:
            when: Date-like value (``date``, ``datetime``, or ISO string) for the transaction.
            amount: Numeric/decimal amount; negative for expenses, positive for income.
            currency: ISO currency code (e.g. ``"EUR"``). Defaults to base currency.
            category: Optional category name. Must be pre-registered via :meth:`add_category`.
            description: Free-text description.
            meta: Optional custom metadata dictionary stored with the transaction.

        Returns:
            The generated transaction ID (UUID string).

        Raises:
            UnknownCategory: If a non-None `category` is not known.
            ValueError: If `amount` is zero.

        Examples:
            Expense in base currency:

            >>> t = PersonalFinanceTracker(base_currency="EUR")
            >>> t.add_category("Dining")
            >>> tx_id = t.add_transaction("2025-08-01", -12.90, category="Dining", description="Lunch")

            Income in foreign currency:

            >>> tx_id = t.add_transaction("2025-08-02", 100, currency="USD", description="Gift")
        """
        self._ensure_open()

        d = to_date(when)
        if category is not None and category not in self._categories:
            raise UnknownCategory(category)
        amt = to_decimal(amount)
        if amt == 0:
            raise ValueError("Amount cannot be zero")
        if currency is None:
            currency = self.base_currency
        tx = Transaction(
            id=str(uuid.uuid4()),
            date=d,
            category=category,
            currency=currency.upper(),
            amount=quantize(amt, currency),
            description=description,
            meta=meta or {},
        )
        self._transactions.append(tx)
        logger.info("Added transaction %s: %s %s (%s)", tx.id, tx.amount, tx.currency, tx.description or "-")
        return tx.id

    def delete_transaction(self, tx_id: str) -> bool:
        """Delete a transaction by its ID.

        Returns True if the transaction was found and removed; otherwise raises
        :class:`UnknownTransaction`.

        Args:
            tx_id: The UUID string returned by :meth:`add_transaction`.

        Returns:
            True if the transaction existed and was deleted.

        Raises:
            UnknownTransaction: If no transaction matches the given ID.

        Examples:
            >>> t = PersonalFinanceTracker()
            >>> tx = t.add_transaction("2025-08-01", -5)
            >>> t.delete_transaction(tx)
            True

            Attempt to delete a non-existing ID:

            >>> t.delete_transaction("00000000-0000-0000-0000-000000000000")
            Traceback (most recent call last):
            UnknownTransaction: ...
        """
        self._ensure_open()

        for i, t in enumerate(self._transactions):
            if t.id == tx_id:
                del self._transactions[i]
                logger.info("Deleted transaction %s", tx_id)
                return True

        logger.warning("Attempted to delete unknown transaction %s", tx_id)
        raise UnknownTransaction(tx_id)

    def list_transactions(
            self,
            *,
            category: Optional[str] = None,
            since: Optional[Any] = None,
            until: Optional[Any] = None,
    ) -> List[Transaction]:
        """Return transactions filtered by category and/or date range.

        Results are sorted by ``(date, id)`` ascending.

        Args:
            category: Optional category name to filter.
            since: Inclusive start date (date-like or ISO string). If omitted, no lower bound.
            until: Inclusive end date (date-like or ISO string). If omitted, no upper bound.

        Returns:
            A list of :class:`pftracker.models.Transaction` objects.

        Examples:
            >>> t = PersonalFinanceTracker()
            >>> t.add_category("Groceries")
            >>> t.add_transaction("2025-08-01", -10, category="Groceries")
            >>> t.add_transaction("2025-08-05", -15, category="Groceries")
            >>> [tr.amount for tr in t.list_transactions(category="Groceries")]
            [Decimal('-10'), Decimal('-15')]

            Date filtering:

            >>> [tr.amount for tr in t.list_transactions(since="2025-08-02", until="2025-08-31")]
            [Decimal('-15')]
        """
        self._ensure_open()

        s = to_date(since) if since else None
        u = to_date(until) if until else None
        out = []
        for t in self._transactions:
            if category and t.category != category:
                continue
            if s and t.date < s:
                continue
            if u and t.date > u:
                continue
            out.append(t)
        return sorted(out, key=lambda tx: (tx.date, tx.id))

    def balance(self) -> Decimal:
        """Compute the current wallet balance in base currency.

        Sums all transactions converted to the base currency using their transaction dates.

        Returns:
            The current balance as a :class:`decimal.Decimal` quantized to base currency.

        Examples:
            >>> t = PersonalFinanceTracker(base_currency="EUR")
            >>> t.add_transaction("2025-08-01", 100)     # income
            >>> t.add_transaction("2025-08-02", -30)     # expense
            >>> t.balance()
            Decimal('70')
        """
        self._ensure_open()

        total = Decimal("0")
        for t in self._transactions:
            total += self._convert(t.amount, t.currency, self.base_currency, t.date)
        bal = quantize(total, self.base_currency)
        logger.info("Computed balance: %s %s", bal, self.base_currency)
        return bal

    # ------------------------- Budget ---------------------------
    def set_budget(self, month: str, category: str, amount: Any, currency: Optional[str] = None) -> None:
        """Define or update a monthly budget for a category.

        The budget is stored in the tracker's base currency. If `currency` is provided,
        `amount` is converted to base currency using :meth:`convert`.

        Args:
            month: Month in ``"YYYY-MM"`` format.
            category: Existing category for which the budget is set.
            amount: Budget amount (numeric/decimal).
            currency: Currency of `amount`. Defaults to base currency.

        Raises:
            UnknownCategory: If `category` is unknown.
            ValueError: If `month` is not of the form ``"YYYY-MM"``.

        Examples:
            >>> t = PersonalFinanceTracker(base_currency="EUR")
            >>> t.add_category("Groceries")
            >>> t.set_budget("2025-08", "Groceries", 300)
            >>> status = t.budget_status("2025-08")
            >>> status["Groceries"]["budget"]
            Decimal('300')
        """
        self._ensure_open()

        if category not in self._categories:
            raise UnknownCategory(category)

        try:
            y, m = month.split("-")
            month_key_val = f"{int(y):04d}-{int(m):02d}"
        except Exception as e:
            raise ValueError("month must be 'YYYY-MM' or a date") from e

        amt = to_decimal(amount)
        cur = (currency or self.base_currency).upper()
        base_amt = self._convert(amt, cur, self.base_currency)
        self._budgets[(month_key_val, category)] = quantize(base_amt, self.base_currency)
        logger.info("Set budget for %s/%s to %s %s", month_key_val, category, base_amt, self.base_currency)

    def budget_status(self, month: str) -> Dict[str, Dict[str, Decimal]]:
        """Get budget consumption per category for a given month.

        Returns a mapping:
        ``{category: {"budget": Decimal, "spent": Decimal, "remaining": Decimal}}``
        where all values are in base currency. Expenses (negative amounts) contribute
        positively to ``"spent"``.

        Args:
            month: Month in ``"YYYY-MM"`` format.

        Returns:
            A dictionary with per-category budget, spent, and remaining decimals.

        Raises:
            ValueError: If `month` is not of the form ``"YYYY-MM"``.

        Examples:
            >>> t = PersonalFinanceTracker(base_currency="EUR")
            >>> t.add_category("Dining")
            >>> t.set_budget("2025-08", "Dining", 200)
            >>> t.add_transaction("2025-08-10", -25, category="Dining")
            >>> t.add_transaction("2025-08-12", -15, category="Dining")
            >>> s = t.budget_status("2025-08")
            >>> (s["Dining"]["spent"], s["Dining"]["remaining"])
            (Decimal('40'), Decimal('160'))
        """
        self._ensure_open()

        try:
            y, m = month.split("-")
            month_key_val = f"{int(y):04d}-{int(m):02d}"
            year, mon = int(y), int(m)
        except Exception as e:
            raise ValueError("month must be 'YYYY-MM' or a date") from e
        start = date(year, mon, 1)

        # Compute end (exclusive)
        if start.month == 12:
            end = date(start.year + 1, 1, 1)
        else:
            end = date(start.year, start.month + 1, 1)

        # Sum expenses per category in base currency
        spent: Dict[str, Decimal] = {}
        for t in self.list_transactions(since=start, until=end - timedelta(days=1)):
            if t.category is None:
                continue
            amt_base = self._convert(t.amount, t.currency, self.base_currency, t.date)
            if t.amount < 0:  # expense
                spent[t.category] = spent.get(t.category, Decimal("0")) + (-amt_base)

        out: Dict[str, Dict[str, Decimal]] = {}
        cats = {cat for (m, cat) in self._budgets.keys() if m == month_key_val} | set(spent.keys())
        for cat in cats:
            budget = self._budgets.get((month_key_val, cat), Decimal("0"))
            s = quantize(spent.get(cat, Decimal("0")), self.base_currency)
            remaining = quantize(budget - s, self.base_currency)
            out[cat] = {"budget": budget, "spent": s, "remaining": remaining}
        logger.info("Computed budget status for %s", month_key_val)
        return out

    # ------------------------- Conversions ---------------------------------
    def _convert(self, amount: Decimal, from_currency: str, to_currency: str, on: Optional[date] = None) -> Decimal:
        """Convert an amount between currencies."""
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()
        if from_currency == to_currency:
            return quantize(amount, to_currency)
        rate = self._get_convertion_rate(from_currency=from_currency, to_currency=to_currency, on=on)
        res = quantize(amount * rate, to_currency)
        logger.debug(
            "Converted %s %s -> %s %s at rate %s (on=%s)",
            amount, from_currency, res, to_currency, rate, on,
        )
        return res

    def _get_convertion_rate(self, *args, **kwargs):
        return self.exchange.get_rate(*args, **kwargs)

    # ------------------------- Persistence ---------------------------------
    def close(self) -> None:
        """Persist current state and release the storage backend.

        This method flushes in-memory data to the storage via :meth:`save` and then
        calls ``storage.close()``.

        Examples:
            >>> t = PersonalFinanceTracker()
            >>> try:
            ...     t.add_transaction("2025-08-01", 1)
            ... finally:
            ...     t.close()
        """
        if self._closed:
            return
        self.save()
        self.storage.close()
        self._closed = True

    def _ensure_open(self) -> None:
        """Ensure that the tracker is still open.

        Raises:
            RuntimeError: If the tracker has already been closed.
        """
        if self._closed:
            raise RuntimeError("Tracker is closed. Start tracker again or use a context manager.")

    def __enter__(self):
        """Enter the context manager, returning ``self``.

        Returns:
            The tracker instance.

        Examples:
            >>> with PersonalFinanceTracker() as t:
            ...     _ = t.balance()
        """
        return self

    def __exit__(self, exc_type, exc, tb):
        """Exit the context manager, ensuring the correct tracker closing."""
        self.close()

    def save(self) -> None:
        """Persist the current tracker state to the configured storage backend.

        This method writes all transactions, budgets, categories, and the base
        currency into the storage. It does **not** release the storage lock;
        you must call :meth:`close` when finished, or (recommended) use the
        tracker in a ``with`` statement so it auto-saves and closes.

        Examples:
            Manual save (rarely needed, since :meth:`close` or the context
            manager will save automatically):

            >>> with PersonalFinanceTracker(base_currency="EUR") as t:
            ...     t.add_category("Groceries")
            ...     t.add_transaction("2025-08-01", -15, category="Groceries")
            ...     t.save()  # explicitly save intermediate state
        """
        self._ensure_open()

        payload = {
            "base_currency": self.base_currency,
            "transactions": [t.to_dict() for t in self._transactions],
            "budgets": {f"{m}|{c}": str(v) for (m, c), v in self._budgets.items()},
            "categories": sorted(self._categories),
        }
        self.storage.save(payload)
        logger.info("Saved state to %s", getattr(self.storage, "path", self.storage))

    def _load_from_dict(self, data: Dict[str, Any]) -> None:
        self.base_currency = data.get("base_currency", self.base_currency)
        self._transactions = [Transaction.from_dict(d) for d in data.get("transactions", [])]
        self._budgets = {}
        for k, v in data.get("budgets", {}).items():
            month_str, cat = k.split("|")
            self._budgets[(month_str, cat)] = to_decimal(v)
        self._categories = set(data.get("categories", []))
