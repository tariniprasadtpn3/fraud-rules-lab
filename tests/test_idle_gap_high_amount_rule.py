from datetime import datetime, timedelta

import pytest

from src.generator import Transaction
from src.rules import IdleGapHighAmountRule, Rule

START = datetime(2026, 3, 2, 12, 0)


def _txn(day: float, amount: float) -> Transaction:
    return Transaction("T", "ACC0001", START + timedelta(days=day), amount, "grocery", "IN")


def test_implements_interface():
    assert isinstance(IdleGapHighAmountRule(), Rule)
    assert IdleGapHighAmountRule().name == "idle_gap_high_amount"


def test_flags_large_amount_after_gap():
    assert IdleGapHighAmountRule().evaluate(_txn(10, 900.0), [_txn(0, 20.0)]) is True


def test_gap_exactly_at_limit_is_flagged():
    assert IdleGapHighAmountRule().evaluate(_txn(5, 900.0), [_txn(0, 20.0)]) is True


def test_short_gap_not_flagged():
    assert IdleGapHighAmountRule().evaluate(_txn(4, 900.0), [_txn(0, 20.0)]) is False


def test_amount_at_threshold_not_flagged():
    assert IdleGapHighAmountRule().evaluate(_txn(10, 500.0), [_txn(0, 20.0)]) is False


def test_uses_most_recent_transaction_for_gap():
    hist = [_txn(0, 20.0), _txn(9, 20.0)]
    assert IdleGapHighAmountRule().evaluate(_txn(10, 900.0), hist) is False


def test_no_history_not_flagged():
    assert IdleGapHighAmountRule().evaluate(_txn(10, 9999.0), []) is False


def test_invalid_parameters():
    with pytest.raises(ValueError):
        IdleGapHighAmountRule(threshold=0)
    with pytest.raises(ValueError):
        IdleGapHighAmountRule(gap_days=0)
