from datetime import datetime

import pytest

from src.generator import Transaction
from src.rules import Rule, WeekendHighAmountRule

SATURDAY = datetime(2026, 3, 7, 14, 0)
SUNDAY = datetime(2026, 3, 8, 14, 0)
MONDAY = datetime(2026, 3, 9, 14, 0)


def _txn(ts: datetime, amount: float) -> Transaction:
    return Transaction("T1", "ACC0001", ts, amount, "grocery", "IN")


def test_implements_interface():
    assert isinstance(WeekendHighAmountRule(), Rule)
    assert WeekendHighAmountRule().name == "weekend_high_amount"


def test_flags_large_saturday_and_sunday():
    rule = WeekendHighAmountRule()
    assert rule.evaluate(_txn(SATURDAY, 800.0), []) is True
    assert rule.evaluate(_txn(SUNDAY, 800.0), []) is True


def test_weekday_not_flagged():
    assert WeekendHighAmountRule().evaluate(_txn(MONDAY, 800.0), []) is False


def test_small_weekend_amount_not_flagged():
    assert WeekendHighAmountRule().evaluate(_txn(SATURDAY, 499.99), []) is False


def test_exactly_at_threshold_flagged():
    assert WeekendHighAmountRule().evaluate(_txn(SATURDAY, 500.0), []) is True


def test_invalid_threshold():
    with pytest.raises(ValueError):
        WeekendHighAmountRule(threshold=0)
