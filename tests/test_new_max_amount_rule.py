from datetime import datetime, timedelta

import pytest

from src.generator import Transaction
from src.rules import NewMaxAmountRule, Rule

T0 = datetime(2026, 3, 1, 12, 0)


def _txn(i: int, amount: float) -> Transaction:
    return Transaction(f"T{i}", "ACC0001", T0 + timedelta(hours=i), amount, "grocery", "IN")


def _hist(amounts):
    return [_txn(i, a) for i, a in enumerate(amounts)]


def test_implements_interface():
    assert isinstance(NewMaxAmountRule(), Rule)
    assert NewMaxAmountRule().name == "new_max_amount"


def test_flags_amount_far_above_history_max():
    assert NewMaxAmountRule().evaluate(_txn(9, 500.0), _hist([40, 50, 60, 80, 100])) is True


def test_amount_below_threshold_not_flagged():
    assert NewMaxAmountRule().evaluate(_txn(9, 140.0), _hist([40, 50, 60, 80, 100])) is False


def test_exactly_at_threshold_not_flagged():
    assert NewMaxAmountRule().evaluate(_txn(9, 150.0), _hist([40, 50, 60, 80, 100])) is False


def test_short_history_not_flagged():
    assert NewMaxAmountRule().evaluate(_txn(9, 500.0), _hist([40, 50, 60, 80])) is False


def test_invalid_parameters():
    with pytest.raises(ValueError):
        NewMaxAmountRule(factor=1.0)
    with pytest.raises(ValueError):
        NewMaxAmountRule(min_history=0)
