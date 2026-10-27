from datetime import datetime, timedelta

import pytest

from src.generator import Transaction
from src.rules import NewAccountHighAmountRule, Rule


def _txn(i: int, amount: float) -> Transaction:
    ts = datetime(2026, 3, 1, 12, 0) + timedelta(days=i)
    return Transaction(f"T{i}", "ACC0001", ts, amount, "grocery", "IN")


def _history(n: int):
    return [_txn(i, 20.0) for i in range(n)]


def test_implements_interface():
    assert isinstance(NewAccountHighAmountRule(), Rule)
    assert NewAccountHighAmountRule().name == "new_account_high_amount"


def test_flags_large_first_transaction():
    assert NewAccountHighAmountRule().evaluate(_txn(0, 1500.0), []) is True


def test_threshold_is_inclusive():
    assert NewAccountHighAmountRule().evaluate(_txn(1, 1000.0), _history(1)) is True


def test_small_amount_not_flagged():
    assert NewAccountHighAmountRule().evaluate(_txn(1, 999.99), _history(1)) is False


def test_established_account_not_flagged():
    assert NewAccountHighAmountRule().evaluate(_txn(3, 5000.0), _history(3)) is False


def test_invalid_parameters():
    with pytest.raises(ValueError):
        NewAccountHighAmountRule(threshold=0)
    with pytest.raises(ValueError):
        NewAccountHighAmountRule(max_history=0)
