from datetime import datetime, timedelta

import pytest

from src.generator import Transaction
from src.rules import AmountZScoreRule, Rule

T0 = datetime(2026, 3, 1, 12, 0)


def _txn(i: int, amount: float) -> Transaction:
    return Transaction(f"T{i}", "ACC0001", T0 + timedelta(hours=i), amount, "grocery", "IN")


def _hist(amounts):
    return [_txn(i, a) for i, a in enumerate(amounts)]


STEADY = [40.0, 42.0, 38.0, 41.0, 39.0] * 2  # mean 40, stdev ~1.4


def test_implements_interface():
    assert isinstance(AmountZScoreRule(), Rule)
    assert AmountZScoreRule().name == "amount_zscore"


def test_flags_outlier_for_steady_account():
    assert AmountZScoreRule().evaluate(_txn(99, 60.0), _hist(STEADY)) is True


def test_normal_amount_not_flagged():
    assert AmountZScoreRule().evaluate(_txn(99, 41.0), _hist(STEADY)) is False


def test_same_amount_is_normal_for_volatile_account():
    volatile = [10.0, 90.0, 20.0, 80.0, 30.0, 70.0, 15.0, 85.0, 25.0, 75.0]
    assert AmountZScoreRule().evaluate(_txn(99, 100.0), _hist(volatile)) is False


def test_zero_spread_not_flagged():
    assert AmountZScoreRule().evaluate(_txn(99, 500.0), _hist([40.0] * 10)) is False


def test_short_history_not_flagged():
    assert AmountZScoreRule().evaluate(_txn(99, 5000.0), _hist(STEADY[:9])) is False


def test_invalid_parameters():
    with pytest.raises(ValueError):
        AmountZScoreRule(threshold=0)
    with pytest.raises(ValueError):
        AmountZScoreRule(min_history=1)
