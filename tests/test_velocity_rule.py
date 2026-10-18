from datetime import datetime, timedelta

import pytest

from src.generator import VELOCITY, Transaction, generate_transactions
from src.rules import Rule, VelocityRule

T0 = datetime(2026, 3, 1, 12, 0, 0)


def _txn(seconds: int, i: int = 0) -> Transaction:
    return Transaction(f"T{i}", "ACC0001", T0 + timedelta(seconds=seconds), 100.0, "dining", "IN")


def test_velocity_rule_implements_interface():
    assert isinstance(VelocityRule(), Rule)
    assert VelocityRule().name == "velocity"


def test_not_flagged_below_threshold():
    history = [_txn(0, 1)]
    assert VelocityRule().evaluate(_txn(30, 2), history) is False


def test_flagged_at_threshold():
    history = [_txn(0, 1), _txn(60, 2)]
    assert VelocityRule().evaluate(_txn(120, 3), history) is True


def test_old_transactions_outside_window_ignored():
    history = [_txn(0, 1), _txn(10, 2)]
    assert VelocityRule().evaluate(_txn(3600, 3), history) is False


def test_invalid_parameters_rejected():
    with pytest.raises(ValueError):
        VelocityRule(min_count=1)
    with pytest.raises(ValueError):
        VelocityRule(window=timedelta(0))


def test_flags_injected_bursts_and_no_normal_traffic():
    txns = generate_transactions(n_accounts=100, days=30, seed=42)
    rule = VelocityRule()
    history: dict = {}
    flagged = []
    for t in txns:
        prior = history.setdefault(t.account_id, [])
        if rule.evaluate(t, prior):
            flagged.append(t)
        prior.append(t)
    assert flagged, "expected at least one burst to be flagged"
    assert all(t.fraud_pattern == VELOCITY for t in flagged)
