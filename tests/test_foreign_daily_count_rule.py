from datetime import datetime, timedelta

import pytest

from src.generator import Transaction
from src.rules import ForeignDailyCountRule, Rule

DAY = datetime(2026, 3, 9, 8, 0)


def _txn(country: str, ts: datetime, amount: float = 20.0) -> Transaction:
    return Transaction("T1", "ACC0001", ts, amount, "grocery", country)


OLD = [_txn("IN", DAY - timedelta(days=3, hours=i)) for i in range(6)]
TODAY = [_txn("IN", DAY + timedelta(minutes=i)) for i in range(4)]


def test_implements_interface():
    assert isinstance(ForeignDailyCountRule(), Rule)
    assert ForeignDailyCountRule().name == "foreign_daily_count"


def test_flags_busy_day_ending_abroad():
    now = _txn("US", DAY + timedelta(hours=5))
    assert ForeignDailyCountRule().evaluate(now, OLD + TODAY) is True


def test_too_few_same_day_not_flagged():
    now = _txn("US", DAY + timedelta(hours=5))
    assert ForeignDailyCountRule().evaluate(now, OLD + TODAY[:3]) is False


def test_other_days_do_not_count():
    now = _txn("US", DAY + timedelta(days=1))
    assert ForeignDailyCountRule().evaluate(now, OLD + TODAY) is False


def test_home_country_not_flagged():
    now = _txn("IN", DAY + timedelta(hours=5))
    assert ForeignDailyCountRule().evaluate(now, OLD + TODAY) is False


def test_needs_min_history():
    now = _txn("US", DAY + timedelta(hours=5))
    assert ForeignDailyCountRule().evaluate(now, TODAY) is False
    assert ForeignDailyCountRule(min_history=4).evaluate(now, TODAY) is True


def test_invalid_parameters():
    with pytest.raises(ValueError):
        ForeignDailyCountRule(max_per_day=1)
    with pytest.raises(ValueError):
        ForeignDailyCountRule(min_history=0)
