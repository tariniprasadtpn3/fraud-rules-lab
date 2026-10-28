from datetime import datetime, timedelta

import pytest

from src.generator import Transaction
from src.rules import NewHourHighAmountRule, Rule


def _txn(i: int, amount: float = 50.0, hour: int = 12) -> Transaction:
    ts = datetime(2026, 3, 1, hour, 0) + timedelta(days=i)
    return Transaction(f"T{i}", "ACC0001", ts, amount, "grocery", "IN")


def _history(n: int = 10):
    return [_txn(i) for i in range(n)]


def test_implements_interface():
    assert isinstance(NewHourHighAmountRule(), Rule)
    assert NewHourHighAmountRule().name == "new_hour_high_amount"


def test_flags_large_amount_at_new_hour():
    assert NewHourHighAmountRule().evaluate(_txn(20, 400.0, 3), _history()) is True


def test_amount_at_threshold_flagged():
    assert NewHourHighAmountRule().evaluate(_txn(20, 300.0, 3), _history()) is True


def test_small_amount_at_new_hour_not_flagged():
    assert NewHourHighAmountRule().evaluate(_txn(20, 299.0, 3), _history()) is False


def test_large_amount_at_known_hour_not_flagged():
    assert NewHourHighAmountRule().evaluate(_txn(20, 900.0, 12), _history()) is False


def test_too_little_history():
    assert NewHourHighAmountRule().evaluate(_txn(20, 900.0, 3), _history(9)) is False


def test_invalid_parameters():
    with pytest.raises(ValueError):
        NewHourHighAmountRule(threshold=0)
    with pytest.raises(ValueError):
        NewHourHighAmountRule(min_history=0)
