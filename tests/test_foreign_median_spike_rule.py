from datetime import datetime, timedelta

import pytest

from src.generator import Transaction
from src.rules import ForeignMedianSpikeRule, Rule

LAST = datetime(2026, 3, 9, 14, 0)


def _txn(amount: float, country: str, ts: datetime = LAST) -> Transaction:
    return Transaction("T1", "ACC0001", ts, amount, "grocery", country)


# Median of these amounts is 40.
HISTORY = [_txn(a, "IN", LAST - timedelta(hours=6 - i)) for i, a in enumerate([30, 35, 40, 40, 45, 50])]


def test_implements_interface():
    assert isinstance(ForeignMedianSpikeRule(), Rule)
    assert ForeignMedianSpikeRule().name == "foreign_median_spike"


def test_flags_large_amount_abroad():
    assert ForeignMedianSpikeRule().evaluate(_txn(250.0, "US"), HISTORY) is True


def test_amount_at_limit_is_not_flagged():
    assert ForeignMedianSpikeRule().evaluate(_txn(200.0, "US"), HISTORY) is False


def test_ignores_home_country():
    assert ForeignMedianSpikeRule().evaluate(_txn(250.0, "IN"), HISTORY) is False


def test_ignores_small_amount_abroad():
    assert ForeignMedianSpikeRule().evaluate(_txn(60.0, "US"), HISTORY) is False


def test_needs_min_history():
    assert ForeignMedianSpikeRule(min_history=7).evaluate(_txn(250.0, "US"), HISTORY) is False
    assert ForeignMedianSpikeRule(min_history=6).evaluate(_txn(250.0, "US"), HISTORY) is True


def test_invalid_parameters():
    with pytest.raises(ValueError):
        ForeignMedianSpikeRule(multiplier=1.0)
    with pytest.raises(ValueError):
        ForeignMedianSpikeRule(min_history=0)
