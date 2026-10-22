from datetime import datetime, timedelta

import pytest

from src.generator import Transaction
from src.rules import RepeatAmountRule, Rule

T0 = datetime(2026, 3, 1, 12, 0)


def _txn(i: int, minutes: float, amount: float) -> Transaction:
    return Transaction(f"T{i}", "ACC0001", T0 + timedelta(minutes=minutes), amount, "dining", "IN")


def test_implements_interface():
    assert isinstance(RepeatAmountRule(), Rule)
    assert RepeatAmountRule().name == "repeat_amount"


def test_flags_same_amount_in_window():
    assert RepeatAmountRule().evaluate(_txn(2, 5, 49.99), [_txn(1, 0, 49.99)]) is True


def test_window_boundary_inclusive():
    rule = RepeatAmountRule(window=timedelta(minutes=10))
    assert rule.evaluate(_txn(2, 10, 20.0), [_txn(1, 0, 20.0)]) is True
    assert rule.evaluate(_txn(2, 10.1, 20.0), [_txn(1, 0, 20.0)]) is False


def test_different_amount_not_flagged():
    assert RepeatAmountRule().evaluate(_txn(2, 1, 20.01), [_txn(1, 0, 20.0)]) is False


def test_empty_history_not_flagged():
    assert RepeatAmountRule().evaluate(_txn(1, 0, 20.0), []) is False


def test_rejects_bad_window():
    with pytest.raises(ValueError):
        RepeatAmountRule(window=timedelta(0))
