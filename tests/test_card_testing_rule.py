from datetime import datetime, timedelta

import pytest

from src.generator import Transaction
from src.rules import CardTestingRule, Rule

T0 = datetime(2026, 3, 1, 12, 0, 0)


def _txn(seconds: int, amount: float = 1.0, i: int = 0) -> Transaction:
    return Transaction(f"T{i}", "ACC0001", T0 + timedelta(seconds=seconds), amount, "dining", "IN")


def test_implements_interface():
    assert isinstance(CardTestingRule(), Rule)
    assert CardTestingRule().name == "card_testing"


def test_flags_third_small_transaction_in_window():
    history = [_txn(0, 1.0, 1), _txn(60, 2.0, 2)]
    assert CardTestingRule().evaluate(_txn(120, 1.5, 3), history) is True


def test_not_flagged_below_count():
    assert CardTestingRule().evaluate(_txn(60, 1.0, 2), [_txn(0, 1.0, 1)]) is False


def test_large_current_amount_not_flagged():
    history = [_txn(0, 1.0, 1), _txn(60, 1.0, 2)]
    assert CardTestingRule().evaluate(_txn(120, 50.0, 3), history) is False


def test_large_history_amounts_do_not_count():
    history = [_txn(0, 100.0, 1), _txn(60, 100.0, 2)]
    assert CardTestingRule().evaluate(_txn(120, 1.0, 3), history) is False


def test_old_small_transactions_outside_window_ignored():
    history = [_txn(0, 1.0, 1), _txn(10, 1.0, 2)]
    assert CardTestingRule().evaluate(_txn(3600, 1.0, 3), history) is False


def test_invalid_parameters_rejected():
    with pytest.raises(ValueError):
        CardTestingRule(max_amount=0)
    with pytest.raises(ValueError):
        CardTestingRule(min_count=1)
    with pytest.raises(ValueError):
        CardTestingRule(window=timedelta(0))
