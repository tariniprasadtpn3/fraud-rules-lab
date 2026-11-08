from datetime import datetime, timedelta

import pytest

from src.generator import Transaction
from src.rules import ForeignPreviousAmountJumpRule, Rule

LAST = datetime(2026, 3, 9, 14, 0)


def _txn(amount: float, country: str, ts: datetime = LAST) -> Transaction:
    return Transaction("T1", "ACC0001", ts, amount, "grocery", country)


HISTORY = [_txn(50.0, "IN", LAST - timedelta(hours=6 - i)) for i in range(6)]  # last = 50


def test_implements_interface():
    assert isinstance(ForeignPreviousAmountJumpRule(), Rule)
    assert ForeignPreviousAmountJumpRule().name == "foreign_previous_amount_jump"


def test_flags_foreign_jump():
    assert ForeignPreviousAmountJumpRule().evaluate(_txn(300.0, "US"), HISTORY) is True


def test_ratio_exactly_at_limit_is_flagged():
    assert ForeignPreviousAmountJumpRule().evaluate(_txn(250.0, "US"), HISTORY) is True


def test_small_ratio_not_flagged():
    assert ForeignPreviousAmountJumpRule().evaluate(_txn(249.0, "US"), HISTORY) is False


def test_home_country_not_flagged():
    assert ForeignPreviousAmountJumpRule().evaluate(_txn(900.0, "IN"), HISTORY) is False


def test_only_last_transaction_counts():
    hist = HISTORY[:-1] + [_txn(900.0, "IN")]
    assert ForeignPreviousAmountJumpRule().evaluate(_txn(1000.0, "US"), hist) is False


def test_needs_min_history():
    txn = _txn(900.0, "US")
    assert ForeignPreviousAmountJumpRule().evaluate(txn, HISTORY[:4]) is False
    assert ForeignPreviousAmountJumpRule(min_history=2).evaluate(txn, HISTORY[:2]) is True


def test_invalid_parameters():
    with pytest.raises(ValueError):
        ForeignPreviousAmountJumpRule(ratio=1.0)
    with pytest.raises(ValueError):
        ForeignPreviousAmountJumpRule(min_history=0)
