from datetime import datetime, timedelta

import pytest

from src.generator import Transaction
from src.rules import MedianSpikeRule, Rule

START = datetime(2026, 3, 2, 12, 0)


def _txn(i: int, amount: float) -> Transaction:
    return Transaction(f"T{i}", "ACC0001", START + timedelta(hours=i), amount, "grocery", "IN")


def _history(amounts):
    return [_txn(i, a) for i, a in enumerate(amounts)]


def test_implements_interface():
    assert isinstance(MedianSpikeRule(), Rule)
    assert MedianSpikeRule().name == "median_spike"


def test_flags_amount_far_above_median():
    hist = _history([10, 10, 10, 10, 10])
    assert MedianSpikeRule().evaluate(_txn(9, 60.0), hist) is True


def test_amount_at_limit_not_flagged():
    hist = _history([10, 10, 10, 10, 10])
    assert MedianSpikeRule().evaluate(_txn(9, 50.0), hist) is False


def test_robust_to_earlier_outlier():
    # mean is 208, so a mean-based rule would not flag 600; the median is 10.
    hist = _history([10, 10, 10, 10, 1000])
    assert MedianSpikeRule().evaluate(_txn(9, 600.0), hist) is True


def test_too_little_history():
    hist = _history([10, 10, 10, 10])
    assert MedianSpikeRule().evaluate(_txn(9, 9999.0), hist) is False


def test_invalid_parameters():
    with pytest.raises(ValueError):
        MedianSpikeRule(multiplier=1)
    with pytest.raises(ValueError):
        MedianSpikeRule(min_history=0)
