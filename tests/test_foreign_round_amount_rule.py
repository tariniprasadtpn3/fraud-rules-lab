from datetime import datetime

import pytest

from src.generator import Transaction
from src.rules import ForeignRoundAmountRule, Rule


def _txn(amount: float, country: str) -> Transaction:
    return Transaction("T1", "ACC0001", datetime(2026, 3, 9, 14, 0), amount, "grocery", country)


HISTORY = [_txn(40.0, "IN") for _ in range(6)]


def test_implements_interface():
    assert isinstance(ForeignRoundAmountRule(), Rule)
    assert ForeignRoundAmountRule().name == "foreign_round_amount"


def test_flags_round_amount_abroad():
    assert ForeignRoundAmountRule().evaluate(_txn(1500.0, "US"), HISTORY) is True


def test_ignores_round_amount_at_home():
    assert ForeignRoundAmountRule().evaluate(_txn(1500.0, "IN"), HISTORY) is False


def test_ignores_non_round_or_small_amount_abroad():
    rule = ForeignRoundAmountRule()
    assert rule.evaluate(_txn(1537.25, "US"), HISTORY) is False
    assert rule.evaluate(_txn(500.0, "US"), HISTORY) is False


def test_needs_min_history():
    assert ForeignRoundAmountRule().evaluate(_txn(1500.0, "US"), HISTORY[:4]) is False
    assert ForeignRoundAmountRule(min_history=2).evaluate(_txn(1500.0, "US"), HISTORY[:2]) is True


def test_invalid_parameters():
    with pytest.raises(ValueError):
        ForeignRoundAmountRule(step=0)
    with pytest.raises(ValueError):
        ForeignRoundAmountRule(min_amount=-1)
    with pytest.raises(ValueError):
        ForeignRoundAmountRule(min_history=0)
