from datetime import datetime, timedelta

import pytest

from src.generator import Transaction
from src.rules import DailySpendRule, Rule

START = datetime(2026, 3, 2, 0, 30)


def _txn(hours: float, amount: float = 100.0) -> Transaction:
    return Transaction("T", "ACC0001", START + timedelta(hours=hours), amount, "grocery", "IN")


def test_implements_interface():
    assert isinstance(DailySpendRule(), Rule)
    assert DailySpendRule().name == "daily_spend"


def test_flags_when_total_reaches_limit():
    hist = [_txn(0, 300.0), _txn(1, 300.0)]
    assert DailySpendRule(max_total=1000.0).evaluate(_txn(2, 400.0), hist) is True


def test_below_limit_not_flagged():
    hist = [_txn(0, 300.0), _txn(1, 300.0)]
    assert DailySpendRule(max_total=1000.0).evaluate(_txn(2, 399.0), hist) is False


def test_other_days_do_not_count():
    hist = [_txn(0, 900.0)]
    assert DailySpendRule(max_total=1000.0).evaluate(_txn(25, 200.0), hist) is False


def test_single_large_transaction_flagged():
    assert DailySpendRule(max_total=1000.0).evaluate(_txn(0, 1500.0), []) is True


def test_invalid_limit_rejected():
    with pytest.raises(ValueError):
        DailySpendRule(max_total=0)
