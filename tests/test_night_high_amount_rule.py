from datetime import datetime

import pytest

from src.generator import Transaction
from src.rules import NightHighAmountRule, Rule


def _txn(hour: int, amount: float = 400.0) -> Transaction:
    return Transaction("T1", "ACC0001", datetime(2026, 3, 1, hour, 30), amount, "grocery", "IN")


def test_implements_interface():
    assert isinstance(NightHighAmountRule(), Rule)
    assert NightHighAmountRule().name == "night_high_amount"


def test_flags_large_amount_at_night():
    assert NightHighAmountRule().evaluate(_txn(3), []) is True


def test_amount_at_threshold_flagged():
    assert NightHighAmountRule().evaluate(_txn(3, 300.0), []) is True


def test_small_amount_at_night_not_flagged():
    assert NightHighAmountRule().evaluate(_txn(3, 299.0), []) is False


def test_large_amount_in_daytime_not_flagged():
    assert NightHighAmountRule().evaluate(_txn(14), []) is False


def test_window_end_is_exclusive():
    assert NightHighAmountRule().evaluate(_txn(5), []) is False
    assert NightHighAmountRule().evaluate(_txn(1), []) is True


def test_window_wrapping_midnight():
    rule = NightHighAmountRule(start_hour=23, end_hour=5)
    assert rule.evaluate(_txn(23), []) is True
    assert rule.evaluate(_txn(0), []) is True
    assert rule.evaluate(_txn(5), []) is False


def test_invalid_parameters():
    with pytest.raises(ValueError):
        NightHighAmountRule(threshold=0)
    with pytest.raises(ValueError):
        NightHighAmountRule(start_hour=24)
    with pytest.raises(ValueError):
        NightHighAmountRule(start_hour=2, end_hour=2)
