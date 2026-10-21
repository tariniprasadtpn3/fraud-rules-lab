from datetime import datetime

import pytest

from src.generator import Transaction
from src.rules import RoundAmountRule, Rule


def _txn(amount: float) -> Transaction:
    return Transaction("T1", "ACC0001", datetime(2026, 3, 1, 12, 0), amount, "electronics", "IN")


def test_implements_interface():
    assert isinstance(RoundAmountRule(), Rule)
    assert RoundAmountRule().name == "round_amount"


def test_flags_large_round_amount_and_ignores_history():
    assert RoundAmountRule().evaluate(_txn(2500.0), []) is True


def test_non_round_amount_not_flagged():
    assert RoundAmountRule().evaluate(_txn(2499.99), []) is False
    assert RoundAmountRule().evaluate(_txn(1234.5), []) is False


def test_below_min_amount_not_flagged():
    assert RoundAmountRule().evaluate(_txn(500.0), []) is False


def test_min_amount_boundary_inclusive():
    assert RoundAmountRule().evaluate(_txn(1000.0), []) is True


def test_custom_step():
    rule = RoundAmountRule(step=100.0, min_amount=100.0)
    assert rule.evaluate(_txn(300.0), []) is True
    assert rule.evaluate(_txn(350.0), []) is False


@pytest.mark.parametrize("step,min_amount", [(0, 1000.0), (-5.0, 1000.0), (500.0, -1.0)])
def test_rejects_bad_parameters(step, min_amount):
    with pytest.raises(ValueError):
        RoundAmountRule(step=step, min_amount=min_amount)
