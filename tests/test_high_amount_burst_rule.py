from datetime import datetime, timedelta

import pytest

from src.generator import Transaction
from src.rules import HighAmountBurstRule, Rule

START = datetime(2026, 3, 2, 12, 0)


def _txn(minute: float, amount: float) -> Transaction:
    return Transaction("T", "ACC0001", START + timedelta(minutes=minute), amount, "grocery", "IN")


def test_implements_interface():
    assert isinstance(HighAmountBurstRule(), Rule)
    assert HighAmountBurstRule().name == "high_amount_burst"


def test_flags_third_large_purchase_in_window():
    hist = [_txn(0, 400.0), _txn(10, 500.0)]
    assert HighAmountBurstRule().evaluate(_txn(20, 350.0), hist) is True


def test_two_large_purchases_not_flagged():
    assert HighAmountBurstRule().evaluate(_txn(10, 500.0), [_txn(0, 400.0)]) is False


def test_small_purchases_do_not_count():
    hist = [_txn(0, 400.0), _txn(10, 20.0)]
    assert HighAmountBurstRule().evaluate(_txn(20, 350.0), hist) is False


def test_small_current_amount_not_flagged():
    hist = [_txn(0, 400.0), _txn(10, 500.0)]
    assert HighAmountBurstRule().evaluate(_txn(20, 299.99), hist) is False


def test_old_purchases_outside_window_ignored():
    hist = [_txn(0, 400.0), _txn(10, 500.0)]
    assert HighAmountBurstRule().evaluate(_txn(120, 350.0), hist) is False


def test_window_boundary_is_inclusive():
    hist = [_txn(0, 400.0), _txn(10, 500.0)]
    assert HighAmountBurstRule().evaluate(_txn(60, 350.0), hist) is True


def test_invalid_parameters():
    with pytest.raises(ValueError):
        HighAmountBurstRule(threshold=0)
    with pytest.raises(ValueError):
        HighAmountBurstRule(min_count=1)
    with pytest.raises(ValueError):
        HighAmountBurstRule(window_minutes=0)
