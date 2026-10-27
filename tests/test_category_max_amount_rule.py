from datetime import datetime, timedelta

import pytest

from src.generator import Transaction
from src.rules import CategoryMaxAmountRule, Rule


def _txn(i: int, amount: float, category: str = "grocery") -> Transaction:
    ts = datetime(2026, 3, 1, 12, 0) + timedelta(days=i)
    return Transaction(f"T{i}", "ACC0001", ts, amount, category, "IN")


def _history(n: int, amount: float = 50.0, category: str = "grocery"):
    return [_txn(i, amount, category) for i in range(n)]


def test_implements_interface():
    assert isinstance(CategoryMaxAmountRule(), Rule)
    assert CategoryMaxAmountRule().name == "category_max_amount"


def test_flags_spike_in_category():
    assert CategoryMaxAmountRule().evaluate(_txn(5, 120.0), _history(4)) is True


def test_at_factor_not_flagged():
    assert CategoryMaxAmountRule().evaluate(_txn(5, 100.0), _history(4)) is False


def test_other_category_history_ignored():
    hist = _history(4, 50.0, "travel")
    assert CategoryMaxAmountRule().evaluate(_txn(5, 500.0), hist) is False


def test_too_little_category_history():
    assert CategoryMaxAmountRule().evaluate(_txn(5, 500.0), _history(2)) is False


def test_large_amounts_in_other_category_do_not_matter():
    hist = _history(3) + _history(3, 5000.0, "travel")
    assert CategoryMaxAmountRule().evaluate(_txn(9, 120.0), hist) is True


def test_invalid_parameters():
    with pytest.raises(ValueError):
        CategoryMaxAmountRule(factor=1)
    with pytest.raises(ValueError):
        CategoryMaxAmountRule(min_history=0)
