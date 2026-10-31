from datetime import datetime, timedelta

import pytest

from src.generator import Transaction
from src.rules import PreviousAmountJumpRule, Rule

START = datetime(2026, 3, 2, 12, 0)


def _txn(hour: int, amount: float) -> Transaction:
    return Transaction("T", "ACC0001", START + timedelta(hours=hour), amount, "grocery", "IN")


def test_implements_interface():
    assert isinstance(PreviousAmountJumpRule(), Rule)
    assert PreviousAmountJumpRule().name == "previous_amount_jump"


def test_flags_big_jump():
    assert PreviousAmountJumpRule().evaluate(_txn(1, 600.0), [_txn(0, 50.0)]) is True


def test_ratio_exactly_at_limit_is_flagged():
    assert PreviousAmountJumpRule().evaluate(_txn(1, 500.0), [_txn(0, 100.0)]) is True


def test_small_ratio_not_flagged():
    assert PreviousAmountJumpRule().evaluate(_txn(1, 400.0), [_txn(0, 100.0)]) is False


def test_amount_at_min_not_flagged():
    assert PreviousAmountJumpRule().evaluate(_txn(1, 200.0), [_txn(0, 10.0)]) is False


def test_only_last_transaction_counts():
    hist = [_txn(0, 10.0), _txn(1, 900.0)]
    assert PreviousAmountJumpRule().evaluate(_txn(2, 1000.0), hist) is False


def test_no_history_not_flagged():
    assert PreviousAmountJumpRule().evaluate(_txn(1, 9999.0), []) is False


def test_invalid_parameters():
    with pytest.raises(ValueError):
        PreviousAmountJumpRule(ratio=1.0)
    with pytest.raises(ValueError):
        PreviousAmountJumpRule(min_amount=-1)
