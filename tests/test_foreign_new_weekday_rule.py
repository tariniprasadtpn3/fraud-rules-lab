from datetime import datetime, timedelta

import pytest

from src.generator import Transaction
from src.rules import ForeignNewWeekdayRule, Rule

MONDAY = datetime(2026, 3, 9, 14, 0)


def _txn(country: str, ts: datetime) -> Transaction:
    return Transaction("T1", "ACC0001", ts, 50.0, "grocery", country)


# Ten home purchases on Monday and Tuesday only.
HISTORY = [_txn("IN", MONDAY + timedelta(days=i % 2, weeks=i)) for i in range(10)]


def test_implements_interface():
    assert isinstance(ForeignNewWeekdayRule(), Rule)
    assert ForeignNewWeekdayRule().name == "foreign_new_weekday"


def test_flags_abroad_on_unused_weekday():
    friday = datetime(2026, 5, 15, 10, 0)
    assert ForeignNewWeekdayRule().evaluate(_txn("US", friday), HISTORY) is True


def test_ignores_used_weekday_or_home_country():
    rule = ForeignNewWeekdayRule()
    assert rule.evaluate(_txn("US", MONDAY + timedelta(weeks=20)), HISTORY) is False
    assert rule.evaluate(_txn("IN", datetime(2026, 5, 15, 10, 0)), HISTORY) is False


def test_needs_min_history():
    friday = datetime(2026, 5, 15, 10, 0)
    assert ForeignNewWeekdayRule().evaluate(_txn("US", friday), HISTORY[:9]) is False
    assert ForeignNewWeekdayRule(min_history=2).evaluate(_txn("US", friday), HISTORY[:2]) is True


def test_invalid_parameters():
    with pytest.raises(ValueError):
        ForeignNewWeekdayRule(min_history=0)
