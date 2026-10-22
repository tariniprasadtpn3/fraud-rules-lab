from datetime import datetime, timedelta

import pytest

from src.generator import GEO_MISMATCH, Transaction, generate_transactions
from src.rules import GeoMismatchRule, Rule

T0 = datetime(2026, 3, 1, 12, 0, 0)


def _txn(country: str, i: int = 0) -> Transaction:
    return Transaction(f"T{i}", "ACC0001", T0 + timedelta(hours=i), 100.0, "dining", country)


def _history(n: int = 5, country: str = "IN"):
    return [_txn(country, i) for i in range(n)]


def test_implements_interface():
    assert isinstance(GeoMismatchRule(), Rule)
    assert GeoMismatchRule().name == "geo_mismatch"


def test_foreign_country_flagged():
    assert GeoMismatchRule().evaluate(_txn("US", 99), _history()) is True


def test_home_country_not_flagged():
    assert GeoMismatchRule().evaluate(_txn("IN", 99), _history()) is False


def test_insufficient_history_never_flagged():
    assert GeoMismatchRule().evaluate(_txn("US", 99), _history(4)) is False


def test_home_is_most_common_country():
    history = _history(5, "IN") + [_txn("US", 50)]
    rule = GeoMismatchRule()
    assert rule.evaluate(_txn("US", 99), history) is True
    assert rule.evaluate(_txn("IN", 99), history) is False


def test_invalid_parameters_rejected():
    with pytest.raises(ValueError):
        GeoMismatchRule(min_history=0)


def test_flags_injected_mismatches_and_no_normal_traffic():
    txns = generate_transactions(n_accounts=100, days=30, seed=42)
    rule = GeoMismatchRule()
    history: dict = {}
    flagged = []
    for t in txns:
        prior = history.setdefault(t.account_id, [])
        if rule.evaluate(t, prior):
            flagged.append(t)
        prior.append(t)
    assert flagged
    # country_hop fraud is also made abroad, so it legitimately trips this rule too.
    assert all(t.fraud_pattern in (GEO_MISMATCH, "country_hop") for t in flagged)
    assert any(t.fraud_pattern == GEO_MISMATCH for t in flagged)
