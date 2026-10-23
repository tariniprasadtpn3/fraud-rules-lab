from datetime import datetime, timedelta

import pytest

from src.generator import Transaction
from src.rules import CumulativeSpendRule, Rule

T0 = datetime(2026, 3, 1, 12, 0)


def _txn(i: int, hours: float, amount: float) -> Transaction:
    return Transaction(f"T{i}", "ACC0001", T0 + timedelta(hours=hours), amount, "fashion", "IN")


def test_implements_interface():
    assert isinstance(CumulativeSpendRule(), Rule)
    assert CumulativeSpendRule().name == "cumulative_spend"


def test_flags_when_total_exceeds_limit():
    rule = CumulativeSpendRule(limit=1000.0)
    history = [_txn(1, 0, 400.0), _txn(2, 1, 400.0)]
    assert rule.evaluate(_txn(3, 2, 300.0), history) is True


def test_limit_is_strict():
    rule = CumulativeSpendRule(limit=1000.0)
    assert rule.evaluate(_txn(2, 1, 600.0), [_txn(1, 0, 400.0)]) is False


def test_old_spend_outside_window_ignored():
    rule = CumulativeSpendRule(limit=1000.0, window=timedelta(hours=24))
    assert rule.evaluate(_txn(2, 30, 600.0), [_txn(1, 0, 900.0)]) is False
    assert rule.evaluate(_txn(2, 24, 600.0), [_txn(1, 0, 900.0)]) is True


def test_empty_history_uses_own_amount():
    rule = CumulativeSpendRule(limit=500.0)
    assert rule.evaluate(_txn(1, 0, 501.0), []) is True
    assert rule.evaluate(_txn(1, 0, 500.0), []) is False


def test_rejects_bad_parameters():
    with pytest.raises(ValueError):
        CumulativeSpendRule(limit=0)
    with pytest.raises(ValueError):
        CumulativeSpendRule(window=timedelta(0))
