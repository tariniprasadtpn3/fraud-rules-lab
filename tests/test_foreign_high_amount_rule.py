from datetime import datetime

import pytest

from src.generator import Transaction
from src.rules import ForeignHighAmountRule, Rule

TS = datetime(2026, 3, 9, 14, 0)


def _txn(amount: float, country: str) -> Transaction:
    return Transaction("T1", "ACC0001", TS, amount, "grocery", country)


HISTORY = [_txn(20.0, "IN") for _ in range(6)]


def test_implements_interface():
    assert isinstance(ForeignHighAmountRule(), Rule)
    assert ForeignHighAmountRule().name == "foreign_high_amount"


def test_flags_large_foreign_purchase():
    assert ForeignHighAmountRule().evaluate(_txn(400.0, "US"), HISTORY) is True


def test_small_foreign_purchase_not_flagged():
    assert ForeignHighAmountRule().evaluate(_txn(299.99, "US"), HISTORY) is False


def test_large_home_purchase_not_flagged():
    assert ForeignHighAmountRule().evaluate(_txn(900.0, "IN"), HISTORY) is False


def test_exactly_at_threshold_flagged():
    assert ForeignHighAmountRule().evaluate(_txn(300.0, "US"), HISTORY) is True


def test_short_history_not_flagged():
    assert ForeignHighAmountRule().evaluate(_txn(900.0, "US"), HISTORY[:4]) is False


def test_invalid_params():
    with pytest.raises(ValueError):
        ForeignHighAmountRule(threshold=0)
    with pytest.raises(ValueError):
        ForeignHighAmountRule(min_history=0)
