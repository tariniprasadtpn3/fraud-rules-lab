from datetime import datetime, timedelta

import pytest

from src.generator import Transaction
from src.rules import ForeignIdleGapRule, Rule

LAST = datetime(2026, 3, 9, 14, 0)


def _txn(amount: float, country: str, ts: datetime) -> Transaction:
    return Transaction("T1", "ACC0001", ts, amount, "grocery", country)


HISTORY = [_txn(40.0, "IN", LAST - timedelta(hours=i)) for i in range(5, -1, -1)]


def test_implements_interface():
    assert isinstance(ForeignIdleGapRule(), Rule)
    assert ForeignIdleGapRule().name == "foreign_idle_gap"


def test_flags_foreign_purchase_after_gap():
    txn = _txn(150.0, "US", LAST + timedelta(days=5))
    assert ForeignIdleGapRule().evaluate(txn, HISTORY) is True


def test_ignores_short_gap_or_home_country():
    rule = ForeignIdleGapRule()
    assert rule.evaluate(_txn(150.0, "US", LAST + timedelta(days=4, hours=23)), HISTORY) is False
    assert rule.evaluate(_txn(150.0, "IN", LAST + timedelta(days=9)), HISTORY) is False


def test_ignores_small_amount():
    txn = _txn(99.99, "US", LAST + timedelta(days=9))
    assert ForeignIdleGapRule().evaluate(txn, HISTORY) is False


def test_needs_min_history():
    txn = _txn(150.0, "US", LAST + timedelta(days=9))
    assert ForeignIdleGapRule().evaluate(txn, HISTORY[:4]) is False
    assert ForeignIdleGapRule(min_history=2).evaluate(txn, HISTORY[:2]) is True


def test_invalid_parameters():
    with pytest.raises(ValueError):
        ForeignIdleGapRule(min_amount=-1)
    with pytest.raises(ValueError):
        ForeignIdleGapRule(gap_days=0)
    with pytest.raises(ValueError):
        ForeignIdleGapRule(min_history=0)
