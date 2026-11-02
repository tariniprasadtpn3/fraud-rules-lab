from datetime import datetime

import pytest

from src.generator import Transaction
from src.rules import ForeignWeekendRule, Rule

SATURDAY = datetime(2026, 3, 14, 14, 0)
MONDAY = datetime(2026, 3, 9, 14, 0)


def _txn(amount: float, country: str, ts: datetime = SATURDAY) -> Transaction:
    return Transaction("T1", "ACC0001", ts, amount, "grocery", country)


HISTORY = [_txn(40.0, "IN", MONDAY) for _ in range(6)]


def test_implements_interface():
    assert isinstance(ForeignWeekendRule(), Rule)
    assert ForeignWeekendRule().name == "foreign_weekend"


def test_flags_weekend_purchase_abroad():
    assert ForeignWeekendRule().evaluate(_txn(250.0, "US"), HISTORY) is True
    assert ForeignWeekendRule().evaluate(_txn(250.0, "US", datetime(2026, 3, 15, 9, 0)), HISTORY) is True


def test_ignores_weekday_or_home_country():
    rule = ForeignWeekendRule()
    assert rule.evaluate(_txn(250.0, "US", MONDAY), HISTORY) is False
    assert rule.evaluate(_txn(250.0, "IN"), HISTORY) is False


def test_ignores_small_amount():
    assert ForeignWeekendRule().evaluate(_txn(199.99, "US"), HISTORY) is False


def test_needs_min_history():
    assert ForeignWeekendRule().evaluate(_txn(250.0, "US"), HISTORY[:4]) is False
    assert ForeignWeekendRule(min_history=2).evaluate(_txn(250.0, "US"), HISTORY[:2]) is True


def test_invalid_parameters():
    with pytest.raises(ValueError):
        ForeignWeekendRule(min_amount=-1)
    with pytest.raises(ValueError):
        ForeignWeekendRule(min_history=0)
