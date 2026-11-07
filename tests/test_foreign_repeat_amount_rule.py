from datetime import datetime, timedelta

import pytest

from src.generator import Transaction
from src.rules import ForeignRepeatAmountRule, Rule

LAST = datetime(2026, 3, 9, 14, 0)


def _txn(amount: float, country: str, ts: datetime = LAST) -> Transaction:
    return Transaction("T1", "ACC0001", ts, amount, "grocery", country)


HISTORY = [_txn(40.0 + i, "IN", LAST - timedelta(hours=5 - i)) for i in range(6)]


def test_implements_interface():
    assert isinstance(ForeignRepeatAmountRule(), Rule)
    assert ForeignRepeatAmountRule().name == "foreign_repeat_amount"


def test_flags_repeat_amount_abroad_in_window():
    hist = HISTORY + [_txn(77.0, "US", LAST - timedelta(minutes=5))]
    assert ForeignRepeatAmountRule().evaluate(_txn(77.0, "US"), hist) is True


def test_ignores_repeat_outside_window():
    hist = HISTORY + [_txn(77.0, "US", LAST - timedelta(minutes=30))]
    assert ForeignRepeatAmountRule().evaluate(_txn(77.0, "US"), hist) is False


def test_ignores_different_amount():
    hist = HISTORY + [_txn(77.0, "US", LAST - timedelta(minutes=5))]
    assert ForeignRepeatAmountRule().evaluate(_txn(78.0, "US"), hist) is False


def test_ignores_home_country():
    hist = HISTORY + [_txn(77.0, "IN", LAST - timedelta(minutes=5))]
    assert ForeignRepeatAmountRule().evaluate(_txn(77.0, "IN"), hist) is False


def test_needs_min_history():
    hist = [
        _txn(40.0, "IN", LAST - timedelta(hours=1)),
        _txn(77.0, "US", LAST - timedelta(minutes=5)),
    ]
    assert ForeignRepeatAmountRule(min_history=3).evaluate(_txn(77.0, "US"), hist) is False
    assert ForeignRepeatAmountRule(min_history=2).evaluate(_txn(77.0, "US"), hist) is True


def test_invalid_parameters():
    with pytest.raises(ValueError):
        ForeignRepeatAmountRule(window=timedelta(0))
    with pytest.raises(ValueError):
        ForeignRepeatAmountRule(min_history=0)
