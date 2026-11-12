from datetime import datetime, timedelta

import pytest

from src.generator import Transaction
from src.rules import ForeignDailySpendRule, Rule

DAY = datetime(2026, 3, 9, 8, 0)


def _txn(country: str, ts: datetime, amount: float = 20.0) -> Transaction:
    return Transaction("T1", "ACC0001", ts, amount, "grocery", country)


OLD = [_txn("IN", DAY - timedelta(days=3, hours=i)) for i in range(6)]
TODAY = [_txn("IN", DAY + timedelta(minutes=i), 500.0) for i in range(3)]


def test_implements_interface():
    assert isinstance(ForeignDailySpendRule(), Rule)
    assert ForeignDailySpendRule().name == "foreign_daily_spend"


def test_flags_heavy_day_ending_abroad():
    now = _txn("US", DAY + timedelta(hours=5), 600.0)
    assert ForeignDailySpendRule().evaluate(now, OLD + TODAY) is True


def test_below_threshold_not_flagged():
    now = _txn("US", DAY + timedelta(hours=5), 400.0)
    assert ForeignDailySpendRule().evaluate(now, OLD + TODAY) is False


def test_other_days_do_not_count():
    now = _txn("US", DAY + timedelta(days=1), 600.0)
    assert ForeignDailySpendRule().evaluate(now, OLD + TODAY) is False


def test_home_country_not_flagged():
    now = _txn("IN", DAY + timedelta(hours=5), 600.0)
    assert ForeignDailySpendRule().evaluate(now, OLD + TODAY) is False


def test_needs_min_history():
    now = _txn("US", DAY + timedelta(hours=5), 600.0)
    assert ForeignDailySpendRule().evaluate(now, TODAY) is False
    assert ForeignDailySpendRule(min_history=3).evaluate(now, TODAY) is True


def test_total_exactly_at_threshold_is_flagged():
    now = _txn("US", DAY + timedelta(hours=5), 500.0)
    assert ForeignDailySpendRule().evaluate(now, OLD + TODAY) is True


def test_spend_in_any_country_counts_toward_day_total():
    abroad_today = [_txn("FR", DAY + timedelta(minutes=i), 500.0) for i in range(3)]
    now = _txn("US", DAY + timedelta(hours=5), 600.0)
    assert ForeignDailySpendRule().evaluate(now, OLD + abroad_today) is True


def test_invalid_parameters():
    with pytest.raises(ValueError):
        ForeignDailySpendRule(max_total=0)
    with pytest.raises(ValueError):
        ForeignDailySpendRule(min_history=0)
