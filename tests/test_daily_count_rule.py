from datetime import datetime, timedelta

import pytest

from src.generator import Transaction
from src.rules import DailyCountRule, Rule

START = datetime(2026, 3, 2, 0, 30)


def _txn(hours: float) -> Transaction:
    return Transaction("T", "ACC0001", START + timedelta(hours=hours), 20.0, "grocery", "IN")


def test_implements_interface():
    assert isinstance(DailyCountRule(), Rule)
    assert DailyCountRule().name == "daily_count"


def test_flags_at_limit():
    hist = [_txn(i) for i in range(3)]
    assert DailyCountRule(max_per_day=4).evaluate(_txn(3), hist) is True


def test_below_limit_not_flagged():
    hist = [_txn(i) for i in range(2)]
    assert DailyCountRule(max_per_day=4).evaluate(_txn(2), hist) is False


def test_other_days_do_not_count():
    hist = [_txn(i) for i in range(3)]
    assert DailyCountRule(max_per_day=4).evaluate(_txn(25), hist) is False


def test_no_history_not_flagged():
    assert DailyCountRule().evaluate(_txn(0), []) is False


def test_invalid_limit_rejected():
    with pytest.raises(ValueError):
        DailyCountRule(max_per_day=1)
