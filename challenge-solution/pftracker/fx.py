from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from decimal import Decimal
from typing import Optional

from currency_converter import CurrencyConverter, ECB_URL, RateNotFoundError

from pftracker.models import ExchangeRateError
from pftracker.utils import to_decimal


class ExchangeRateProvider(ABC):
    """Abstract base class for fetching foreign exchange (FX) rates.

    Implementations should return a :class:`Decimal` exchange rate that can be
    used to multiply an amount in ``from_currency`` to obtain its value in
    ``to_currency`` on a given date.
    """

    @abstractmethod
    def get_rate(self, from_currency: str, to_currency: str, on: Optional[date] = None) -> Decimal:
        """Retrieve the FX rate for converting between two currencies.

        Args:
            from_currency: The source currency code (ISO 4217, e.g. ``"USD"``).
            to_currency: The target currency code (ISO 4217, e.g. ``"EUR"``).
            on: The date for which the FX rate is requested.
                If ``None``, the latest available rate is returned.

        Returns:
            Decimal: The conversion rate. Multiply an amount in ``from_currency`` by
            this rate to obtain the amount in ``to_currency``.

        Raises:
            ExchangeRateError: If the implementation cannot provide a rate.
        """
        pass


class ECBRateProvider(ExchangeRateProvider):
    """Exchange rate provider backed by the European Central Bank (ECB).

    Example:
        >>> provider = ECBRateProvider()
        >>> rate = provider.get_rate("USD", "EUR")
        >>> amount_in_eur = Decimal("100") * rate
    """

    def __init__(self):
        self._converter = CurrencyConverter(
            currency_file=ECB_URL,
            fallback_on_wrong_date=True,
            fallback_on_missing_rate=True,
        )

    def get_rate(self, from_currency: str, to_currency: str, on: Optional[date] = None) -> Decimal:
        params = {"from": from_currency.upper(), "to": to_currency.upper()}
        if on is not None:
            params["date"] = on.isoformat()
        try:
            rate = self._converter.convert(1, from_currency, to_currency, date=on)
            return to_decimal(rate)
        except RateNotFoundError as e:
            raise ExchangeRateError(f"Failed to fetch FX rate: {e}") from e
