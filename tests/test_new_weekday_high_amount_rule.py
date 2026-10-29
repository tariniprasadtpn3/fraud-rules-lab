from datetime import datetime, timedelta

import pytest

from src.generator import Transaction
from src.rules import NewWeekdayHighAmountRule, Rule

# 2026-03-02 is a Monday; history covers Monday-Friday only.
MONDAY = datetime(2026, 3, 2, 12, 0)


def _txn(i: int, amount: float = 50.0, day_offset: int | None = None) -> Transaction:
    offset = day_offset if day_offset is not None else i % 5
    ts = MONDAY + timedelta(days=offset)
    return Transaction(f"T{i}", "ACC0001", ts, amount, "grocery", "IN")


def _history(n: int = 14):
    return [_txn(i) for i in range(n)]


def test_implements_interface():
    assert isinstance(NewWeekdayHighAmountRule(), Rule)
    assert NewWeekdayHighAmountRule().name == "new_weekday_high_amount"


def test_flags_large_amount_on_new_weekday():
    # offset 5 -> Saturday, never used in history
    assert NewWeekdayHighAmountRule().evaluate(_txn(30, 400.0, 5), _history()) is True


def test_amount_at_threshold_flagged():
    assert NewWeekdayHighAmountRule().evaluate(_txn(30, 300.0, 5), _history()) is True


def test_small_amount_not_flagged():
    assert NewWeekdayHighAmountRule().evaluate(_txn(30, 299.0, 5), _history()) is False


def test_known_weekday_not_flagged():
    assert NewWeekdayHighAmountRule().evaluate(_txn(30, 900.0, 7), _history()) is False


def test_too_little_history():
    assert NewWeekdayHighAmountRule().evaluate(_txn(30, 900.0, 5), _history(13)) is False


def test_invalid_parameters():
    with pytest.raises(ValueError):
        NewWeekdayHighAmountRule(threshold=0)
    with pytest.raises(ValueError):
        NewWeekdayHighAmountRule(min_history=0)
