from datetime import datetime, timedelta

import pytest

from src.generator import Transaction
from src.rules import CategoryBurstRule, Rule

T0 = datetime(2026, 3, 1, 12, 0)


def _txn(minutes: int, category: str) -> Transaction:
    return Transaction(f"T{minutes}", "ACC0001", T0 + timedelta(minutes=minutes), 25.0, category, "IN")


def test_implements_interface():
    assert isinstance(CategoryBurstRule(), Rule)
    assert CategoryBurstRule().name == "category_burst"


def test_flags_fourth_distinct_category_in_window():
    hist = [_txn(0, "grocery"), _txn(5, "fuel"), _txn(10, "travel")]
    assert CategoryBurstRule().evaluate(_txn(15, "electronics"), hist) is True


def test_repeated_categories_not_flagged():
    hist = [_txn(0, "grocery"), _txn(5, "grocery"), _txn(10, "fuel")]
    assert CategoryBurstRule().evaluate(_txn(15, "fuel"), hist) is False


def test_old_transactions_outside_window_ignored():
    hist = [_txn(0, "grocery"), _txn(1, "fuel"), _txn(2, "travel")]
    assert CategoryBurstRule().evaluate(_txn(120, "electronics"), hist) is False


def test_window_boundary_inclusive():
    hist = [_txn(0, "grocery"), _txn(1, "fuel"), _txn(2, "travel")]
    assert CategoryBurstRule().evaluate(_txn(60, "electronics"), hist) is True


def test_no_history_not_flagged():
    assert CategoryBurstRule().evaluate(_txn(0, "grocery"), []) is False


def test_invalid_parameters():
    with pytest.raises(ValueError):
        CategoryBurstRule(min_categories=1)
    with pytest.raises(ValueError):
        CategoryBurstRule(window=timedelta(0))
