import logging
from datetime import datetime
from decimal import Decimal

import pytest

from pftracker import JsonFileStorage, PersonalFinanceTracker, UnknownCategory, UnknownTransaction


class TestCategories:
    def test_category_available_after_creation(self, tracker):
        tracker.add_category("salary")
        tracker.add_category("groceries")
        assert tracker.list_categories() == ['groceries', 'salary']

    def test_can_be_deleted(self, tracker):
        tracker.add_category("rent")
        tracker.delete_category("rent")
        assert tracker.list_categories() == []

    def test_multiple_categories_deleted(self, tracker):
        tracker.add_category("category1")
        tracker.add_category("category2")
        tracker.add_category("category3")

        tracker.delete_category("category3")
        tracker.delete_category("category1")

        assert tracker.list_categories() == ["category2"]

    def test_delete_category_without_any(self, tracker):
        with pytest.raises(UnknownCategory):
            tracker.delete_category("non_existing_category")

    def test_init_categories_empty(self, tracker):
        init_categories = tracker.list_categories()
        assert init_categories == []

    def test_adding_category_with_empty_name(self, tracker):
        with pytest.raises(ValueError):
            tracker.add_category(name=' ')

    def test_adding_same_category_twice(self, tracker):
        tracker.add_category("rent")
        tracker.add_category("rent")
        assert len(tracker.list_categories()) == 1
        assert tracker.list_categories() == ["rent"]


class TestTransactions:
    def test_positive_balance(self, tracker):
        tracker.add_transaction(when=datetime.now(), amount=Decimal("100.5"))
        tracker.add_transaction(when=datetime.now(), amount=Decimal("50.95"))
        assert tracker.balance() == Decimal("151.45")
        assert len(tracker.list_transactions()) == 2

    def test_negative_balance(self, tracker):
        tracker.add_transaction(when=datetime.now(), amount=Decimal("50.5"))
        tracker.add_transaction(when=datetime.now(), amount=Decimal("-99.999999"))
        assert tracker.balance() == Decimal("-49.50")
        assert len(tracker.list_transactions()) == 2

    def test_transactions_with_category(self, tracker):
        tracker.add_category("rent")
        tracker.add_transaction(when=datetime.now(), amount=Decimal("-100"), category="rent")
        assert len(tracker.list_transactions(category="rent")) == 1

    def test_transactions_with_multiple_categories(self, tracker):
        tracker.add_category("rent")
        tracker.add_category("salary")

        tracker.add_transaction(when="2025-01-01", amount=Decimal("-100"), category="rent")
        tracker.add_transaction(when="2025-02-01", amount=Decimal("-300"), category="rent")
        tracker.add_transaction(when="2025-03-01", amount=Decimal("5000"), category="salary")

        assert len(tracker.list_transactions(category="rent")) == 2
        assert len(tracker.list_transactions(category="salary")) == 1

    def test_transaction_with_unknown_category(self, tracker):
        with pytest.raises(UnknownCategory):
            tracker.add_transaction(when="2025-03-01", amount=Decimal("5000"), category="salary")

    def test_transaction_with_zero_amount(self, tracker):
        with pytest.raises(ValueError):
            tracker.add_transaction(when=datetime.now(), amount=Decimal("0.0"))

    def test_delete_transaction(self, tracker):
        tx1 = tracker.add_transaction(when=datetime.now(), amount=Decimal("10.1"))
        tx2 = tracker.add_transaction(when=datetime.now(), amount=Decimal("-0.91"))
        tx3 = tracker.add_transaction(when=datetime.now(), amount=Decimal("+0.12"))

        tracker.delete_transaction(tx2)

        current_transactions = tracker.list_transactions()
        current_transaction_ids = [tx.id for tx in current_transactions]

        assert len(current_transactions) == 2
        assert tx1 in current_transaction_ids
        assert tx2 not in current_transaction_ids
        assert tx3 in current_transaction_ids

    def test_delete_unknown_transaction(self, tracker):
        with pytest.raises(UnknownTransaction):
            tracker.add_transaction(when=datetime.now(), amount=Decimal("100"))
            tracker.delete_transaction('some-non-existing-transaction-id')

    def test_list_transactions_period(self, tracker):
        tx1 = tracker.add_transaction(when="2024-11-01", amount=Decimal("100.55"))
        tx2 = tracker.add_transaction(when="2024-12-01", amount=Decimal("100.55"))
        tx3 = tracker.add_transaction(when="2025-01-01", amount=Decimal("100.55"))
        tx4 = tracker.add_transaction(when="2025-02-01", amount=Decimal("100.55"))
        tx5 = tracker.add_transaction(when="2025-03-01", amount=Decimal("100.55"))
        tx6 = tracker.add_transaction(when="2025-04-01", amount=Decimal("100.55"))

        selected_transactions = tracker.list_transactions(since="2025-01-01", until="2025-03-31")
        selected_transaction_ids = [tx.id for tx in selected_transactions]

        assert len(selected_transactions) == 3
        assert tx1 not in selected_transaction_ids
        assert tx2 not in selected_transaction_ids
        assert tx3 in selected_transaction_ids
        assert tx4 in selected_transaction_ids
        assert tx5 in selected_transaction_ids
        assert tx6 not in selected_transaction_ids


class TestBudget:
    def test_budget_status_after_transactions(self, tracker):
        tracker.add_category("groceries")
        tracker.set_budget(month="2020-01", category="groceries", amount=Decimal("1200"))
        tracker.add_transaction(when="2020-01-01", amount=Decimal("-54.91"), category="groceries")
        tracker.add_transaction(when="2020-01-15", amount=Decimal("-21.12"), category="groceries")
        tracker.add_transaction(when="2020-01-16", amount=Decimal("-15.23"), category="groceries")
        tracker.add_transaction(when="2020-01-16", amount=Decimal("-1.4"), category="groceries")
        tracker.add_transaction(when="2020-01-31", amount=Decimal("-120.43"), category="groceries")
        groceries_budget = tracker.budget_status("2020-01")["groceries"]
        assert groceries_budget["budget"] == Decimal('1200.00')
        assert groceries_budget["remaining"] == Decimal('986.91')
        assert groceries_budget["spent"] == Decimal('213.09')

    def test_budget_status_without_transactions(self, tracker):
        tracker.add_category("groceries")
        tracker.set_budget(month="2020-01", category="groceries", amount=Decimal("1200"))
        groceries_budget = tracker.budget_status("2020-01")["groceries"]
        assert groceries_budget["budget"] == groceries_budget["remaining"] == Decimal('1200.00')
        assert groceries_budget["spent"] == Decimal('0')

    def test_budget_status_without_setting_budgets(self, tracker):
        assert tracker.budget_status("2020-01") == {}

    def test_budget_unknown_category(self, tracker):
        with pytest.raises(UnknownCategory):
            tracker.set_budget("2020-01", category="some_unknown_category", amount=Decimal("1000"))

    def test_set_budget_wrong_month_format(self, tracker):
        with pytest.raises(ValueError):
            tracker.add_category("groceries")
            tracker.set_budget(month="2020-01-01", category="groceries", amount=Decimal("1200"))

    def test_budget_status_wrong_month_format(self, tracker):
        with pytest.raises(ValueError):
            tracker.budget_status(month="2020-01-01")

    def test_budget_end_of_year(self, tracker):
        tracker.add_category("groceries")
        tracker.set_budget(month="2020-12", category="groceries", amount=Decimal("1200"))
        tracker.add_transaction("2020-11-05", Decimal("-100"), category="groceries")
        tracker.add_transaction("2020-12-01", Decimal("-100"), category="groceries")  # in budget transaction
        tracker.add_transaction("2020-12-31", Decimal("-100"), category="groceries")  # in budget transaction
        tracker.add_transaction("2021-01-01", Decimal("-100"), category="groceries")
        tracker.add_transaction("2021-01-05", Decimal("-100"), category="groceries")

        assert tracker.budget_status("2020-12")["groceries"]["spent"] == Decimal("200")

    def test_budget_considers_only_txs_with_category(self, tracker):
        tracker.add_category("groceries")
        tracker.set_budget(month="2020-05", category="groceries", amount=Decimal("1200"))
        tracker.add_transaction("2020-05-01", Decimal("-100"), category="groceries")
        tracker.add_transaction("2020-05-01", Decimal("-100"))

        assert tracker.budget_status("2020-05")["groceries"]["spent"] == Decimal("100")


class TestConversions:
    @pytest.fixture(autouse=True)
    def mock_convertion_rate(self, monkeypatch):
        monkeypatch.setattr(
            "pftracker.main.PersonalFinanceTracker._get_convertion_rate",
            lambda *args, **kwargs: Decimal("0.9")
        )

    def test_transactions_in_different_currency(self, tracker, mock_convertion_rate):
        tracker.add_transaction(when="2020-01-05", amount=Decimal("100"), currency='USD')
        assert tracker.balance() == Decimal("90")

    def test_budget_in_different_currency(self, tracker, mock_convertion_rate):
        tracker.add_category("groceries")
        tracker.add_transaction(when="2020-01-05", amount=Decimal("-100"), currency='USD',
                                category="groceries")
        tracker.set_budget("2020-01", category="groceries", amount=100)

        groceries_budget = tracker.budget_status("2020-01")["groceries"]

        assert groceries_budget["spent"] == Decimal("90")
        assert groceries_budget["remaining"] == Decimal('10.00')


class TestDefaultCurrency:
    def test_tracker_reports_usd_if_default_currency(self, monkeypatch, storage):
        monkeypatch.setenv("DEFAULT_CURRENCY", "USD")
        with PersonalFinanceTracker(storage=storage) as tracker:
            assert tracker.base_currency == "USD"

    def test_tracker_reports_eur_if_default_currency(self, monkeypatch, storage):
        monkeypatch.setenv("DEFAULT_CURRENCY", "EUR")
        with PersonalFinanceTracker(storage=storage) as tracker:
            assert tracker.base_currency == "EUR"

    def test_tracker_reports_jpy_if_default_currency(self, monkeypatch, storage):
        monkeypatch.setenv("DEFAULT_CURRENCY", "JPY")
        with PersonalFinanceTracker(storage=storage) as tracker:
            assert tracker.base_currency == "JPY"


class TestLogging:
    def test_logging_on_add_and_save(self, tracker, caplog):
        caplog.set_level(logging.INFO, logger="pftracker")
        tracker.add_category("Misc")
        tracker.add_transaction("2025-08-03", Decimal("-12"), currency="EUR",
                                category="Misc", description="Snacks")

        messages = [rec.getMessage() for rec in caplog.records if rec.name == "pftracker"]
        assert any("Added category 'Misc'" in m for m in messages)
        assert any("Added transaction" in m for m in messages)

    def test_delete_unknown_logs_warning(self, tracker, caplog):
        caplog.set_level(logging.WARNING, logger="pftracker")
        with pytest.raises(Exception):
            tracker.delete_transaction("non-existent-id")
        assert any("Attempted to delete unknown transaction" in r.getMessage()
                   for r in caplog.records if r.name == "pftracker")


class TestPersistence:
    @pytest.fixture(scope="class")
    def add_txs(self):
        # factory fixture
        def _add_transactions(tracker):
            tracker.add_category("salary")
            tracker.add_category("rent")
            tracker.add_category("groceries")
            tracker.set_budget(month="2020-05", category="groceries", amount=Decimal("1200"))
            tracker.add_transaction("2020-05-01", Decimal("-100"), category="groceries")
            tracker.add_transaction("2021-05-01", Decimal("-50"), category="groceries")
            tracker.add_transaction("2022-05-01", Decimal("-1"), category="groceries")

        return _add_transactions

    @pytest.fixture(scope="class")
    def reopened_tracker(self, add_txs, tmp_path_factory):
        pftracker_dir = tmp_path_factory.mktemp("pftracker")
        json_storage_path = pftracker_dir / "finance.json"

        with PersonalFinanceTracker(storage=JsonFileStorage(json_storage_path)) as t1:
            add_txs(t1)

        with PersonalFinanceTracker(storage=JsonFileStorage(json_storage_path)) as t2:
            yield t2

    def test_categories_saved(self, reopened_tracker):
        assert reopened_tracker.list_categories() == sorted(["salary", "rent", "groceries"])

    def test_transactions_saved(self, reopened_tracker):
        assert len(reopened_tracker.list_transactions()) == 3

    def test_budget_saved(self, reopened_tracker):
        assert reopened_tracker.budget_status("2020-05")["groceries"]["spent"] == Decimal("100")
