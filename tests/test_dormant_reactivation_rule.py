from datetime import datetime, timedelta

import pytest

from src.generator import DORMANT_REACTIVATION, Transaction, generate_transactions
from src.rules import DormantReactivationRule, Rule

T0 = datetime(2026, 3, 1, 12, 0, 0)


def _txn(day: float, i: int = 0) -> Transaction:
    return Transaction(f"T{i}", "ACC0001", T0 + timedelta(days=day), 100.0, "dining", "IN")


def test_implements_interface():
    assert isinstance(DormantReactivationRule(), Rule)
    assert DormantReactivationRule().name == "dormant_reactivation"


def test_long_gap_flagged():
    assert DormantReactivationRule().evaluate(_txn(20, 9), [_txn(0)]) is True


def test_gap_exactly_at_threshold_flagged():
    assert DormantReactivationRule(14).evaluate(_txn(14, 9), [_txn(0)]) is True


def test_short_gap_not_flagged():
    assert DormantReactivationRule().evaluate(_txn(13, 9), [_txn(0)]) is False


def test_gap_measured_from_latest_transaction():
    history = [_txn(0, 1), _txn(18, 2)]
    assert DormantReactivationRule().evaluate(_txn(20, 9), history) is False


def test_no_history_never_flagged():
    assert DormantReactivationRule().evaluate(_txn(0), []) is False


def test_invalid_parameters_rejected():
    with pytest.raises(ValueError):
        DormantReactivationRule(dormant_days=0)


def test_flags_injected_reactivations_and_no_normal_traffic():
    txns = generate_transactions(n_accounts=100, days=30, seed=42)
    rule = DormantReactivationRule()
    history: dict = {}
    flagged = []
    for t in txns:
        prior = history.setdefault(t.account_id, [])
        if rule.evaluate(t, prior):
            flagged.append(t)
        prior.append(t)
    assert flagged
    assert all(t.fraud_pattern == DORMANT_REACTIVATION for t in flagged)
