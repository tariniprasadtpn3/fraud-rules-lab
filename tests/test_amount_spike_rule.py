from datetime import datetime, timedelta

import pytest

from src.generator import AMOUNT_SPIKE, DORMANT_REACTIVATION, Transaction, generate_transactions
from src.rules import AmountSpikeRule, Rule

T0 = datetime(2026, 3, 1, 12, 0, 0)


def _txn(amount: float, i: int = 0) -> Transaction:
    return Transaction(f"T{i}", "ACC0001", T0 + timedelta(hours=i), amount, "dining", "IN")


def _history(n: int = 5, amount: float = 100.0):
    return [_txn(amount, i) for i in range(n)]


def test_implements_interface():
    assert isinstance(AmountSpikeRule(), Rule)
    assert AmountSpikeRule().name == "amount_spike"


def test_flags_amount_far_above_average():
    assert AmountSpikeRule().evaluate(_txn(1000.0, 99), _history()) is True


def test_normal_amount_not_flagged():
    assert AmountSpikeRule().evaluate(_txn(150.0, 99), _history()) is False


def test_exactly_at_threshold_not_flagged():
    assert AmountSpikeRule().evaluate(_txn(400.0, 99), _history()) is False


def test_insufficient_history_never_flagged():
    assert AmountSpikeRule().evaluate(_txn(10_000.0, 99), _history(4)) is False


def test_invalid_parameters_rejected():
    with pytest.raises(ValueError):
        AmountSpikeRule(multiplier=1.0)
    with pytest.raises(ValueError):
        AmountSpikeRule(min_history=0)


def test_flags_injected_spikes_and_no_normal_traffic():
    txns = generate_transactions(n_accounts=100, days=30, seed=42)
    rule = AmountSpikeRule()
    history: dict = {}
    flagged = []
    for t in txns:
        prior = history.setdefault(t.account_id, [])
        if rule.evaluate(t, prior):
            flagged.append(t)
        prior.append(t)
    assert any(t.fraud_pattern == AMOUNT_SPIKE for t in flagged)
    # Large dormant-account purchases are also big, so they may be flagged too.
    assert all(t.fraud_pattern in (AMOUNT_SPIKE, DORMANT_REACTIVATION) for t in flagged)
