from datetime import datetime, timedelta

import pytest

from src.generator import Transaction
from src.rules import ForeignNewMaxAmountRule, Rule

LAST = datetime(2026, 3, 9, 14, 0)


def _txn(amount: float, country: str, ts: datetime = LAST) -> Transaction:
    return Transaction("T1", "ACC0001", ts, amount, "grocery", country)


HISTORY = [_txn(40.0 + i, "IN", LAST - timedelta(hours=5 - i)) for i in range(6)]  # max 45


def test_implements_interface():
    assert isinstance(ForeignNewMaxAmountRule(), Rule)
    assert ForeignNewMaxAmountRule().name == "foreign_new_max_amount"


def test_flags_foreign_record_amount():
    assert ForeignNewMaxAmountRule().evaluate(_txn(45.01, "US"), HISTORY) is True


def test_ignores_amount_not_above_max():
    assert ForeignNewMaxAmountRule().evaluate(_txn(45.0, "US"), HISTORY) is False


def test_ignores_home_country():
    assert ForeignNewMaxAmountRule().evaluate(_txn(500.0, "IN"), HISTORY) is False


def test_needs_min_history():
    txn = _txn(500.0, "US")
    assert ForeignNewMaxAmountRule().evaluate(txn, HISTORY[:4]) is False
    assert ForeignNewMaxAmountRule(min_history=2).evaluate(txn, HISTORY[:2]) is True


def test_invalid_parameters():
    with pytest.raises(ValueError):
        ForeignNewMaxAmountRule(min_history=0)
