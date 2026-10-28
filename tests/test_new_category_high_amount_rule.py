from datetime import datetime, timedelta

import pytest

from src.generator import Transaction
from src.rules import NewCategoryHighAmountRule, Rule


def _txn(i: int, amount: float = 50.0, category: str = "grocery") -> Transaction:
    ts = datetime(2026, 3, 1, 12, 0) + timedelta(days=i)
    return Transaction(f"T{i}", "ACC0001", ts, amount, category, "IN")


def _history(n: int = 12):
    return [_txn(i) for i in range(n)]


def test_implements_interface():
    assert isinstance(NewCategoryHighAmountRule(), Rule)
    assert NewCategoryHighAmountRule().name == "new_category_high_amount"


def test_flags_large_amount_in_new_category():
    assert NewCategoryHighAmountRule().evaluate(_txn(20, 400.0, "jewelry"), _history()) is True


def test_amount_at_threshold_flagged():
    assert NewCategoryHighAmountRule().evaluate(_txn(20, 300.0, "jewelry"), _history()) is True


def test_small_amount_in_new_category_not_flagged():
    assert NewCategoryHighAmountRule().evaluate(_txn(20, 299.0, "jewelry"), _history()) is False


def test_large_amount_in_known_category_not_flagged():
    assert NewCategoryHighAmountRule().evaluate(_txn(20, 900.0, "grocery"), _history()) is False


def test_previously_used_category_not_flagged():
    hist = _history() + [_txn(13, 20.0, "jewelry")]
    assert NewCategoryHighAmountRule().evaluate(_txn(20, 900.0, "jewelry"), hist) is False


def test_too_little_history():
    assert NewCategoryHighAmountRule().evaluate(_txn(20, 900.0, "jewelry"), _history(9)) is False


def test_invalid_parameters():
    with pytest.raises(ValueError):
        NewCategoryHighAmountRule(threshold=0)
    with pytest.raises(ValueError):
        NewCategoryHighAmountRule(min_history=0)
