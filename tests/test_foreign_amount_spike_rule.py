from datetime import datetime

import pytest

from src.generator import Transaction
from src.rules import ForeignAmountSpikeRule, Rule

TS = datetime(2026, 3, 9, 14, 0)


def _txn(amount: float, country: str) -> Transaction:
    return Transaction("T1", "ACC0001", TS, amount, "grocery", country)


HISTORY = [_txn(40.0, "IN") for _ in range(6)]


def test_implements_interface():
    assert isinstance(ForeignAmountSpikeRule(), Rule)
    assert ForeignAmountSpikeRule().name == "foreign_amount_spike"


def test_flags_large_purchase_abroad():
    assert ForeignAmountSpikeRule().evaluate(_txn(121.0, "US"), HISTORY) is True


def test_ignores_home_country_or_normal_amount():
    rule = ForeignAmountSpikeRule()
    assert rule.evaluate(_txn(500.0, "IN"), HISTORY) is False
    assert rule.evaluate(_txn(120.0, "US"), HISTORY) is False


def test_needs_min_history():
    assert ForeignAmountSpikeRule().evaluate(_txn(500.0, "US"), HISTORY[:4]) is False
    assert ForeignAmountSpikeRule(min_history=2).evaluate(_txn(500.0, "US"), HISTORY[:2]) is True


def test_invalid_parameters():
    with pytest.raises(ValueError):
        ForeignAmountSpikeRule(multiplier=1.0)
    with pytest.raises(ValueError):
        ForeignAmountSpikeRule(min_history=0)
