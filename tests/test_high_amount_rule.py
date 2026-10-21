from datetime import datetime

import pytest

from src.generator import Transaction
from src.rules import HighAmountRule, Rule

T0 = datetime(2026, 3, 1, 12, 0, 0)


def _txn(amount: float) -> Transaction:
    return Transaction("T1", "ACC0001", T0, amount, "electronics", "IN")


def test_implements_interface():
    assert isinstance(HighAmountRule(), Rule)
    assert HighAmountRule().name == "high_amount"


def test_flags_amount_above_threshold_without_history():
    assert HighAmountRule(threshold=1000.0).evaluate(_txn(1000.01), []) is True


def test_threshold_is_exclusive():
    assert HighAmountRule(threshold=1000.0).evaluate(_txn(1000.0), []) is False


def test_small_amount_not_flagged():
    assert HighAmountRule().evaluate(_txn(20.0), []) is False


@pytest.mark.parametrize("bad", [0, -5.0])
def test_rejects_non_positive_threshold(bad):
    with pytest.raises(ValueError):
        HighAmountRule(threshold=bad)
