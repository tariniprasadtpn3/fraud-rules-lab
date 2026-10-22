from datetime import datetime, timedelta

import pytest

from src.generator import Transaction
from src.rules import CountryHopRule, Rule

T0 = datetime(2026, 3, 1, 12, 0)


def _txn(i: int, minutes: float, country: str) -> Transaction:
    return Transaction(f"T{i}", "ACC0001", T0 + timedelta(minutes=minutes), 30.0, "dining", country)


def test_implements_interface():
    assert isinstance(CountryHopRule(), Rule)
    assert CountryHopRule().name == "country_hop"


def test_flags_quick_country_change():
    assert CountryHopRule().evaluate(_txn(2, 30, "US"), [_txn(1, 0, "IN")]) is True


def test_same_country_not_flagged():
    assert CountryHopRule().evaluate(_txn(2, 30, "IN"), [_txn(1, 0, "IN")]) is False


def test_slow_country_change_not_flagged():
    assert CountryHopRule().evaluate(_txn(2, 600, "US"), [_txn(1, 0, "IN")]) is False


def test_window_boundary_inclusive():
    rule = CountryHopRule(window=timedelta(hours=1))
    assert rule.evaluate(_txn(2, 60, "GB"), [_txn(1, 0, "IN")]) is True
    assert rule.evaluate(_txn(2, 60.5, "GB"), [_txn(1, 0, "IN")]) is False


def test_only_latest_transaction_is_compared():
    history = [_txn(1, 0, "US"), _txn(2, 10, "IN")]
    assert CountryHopRule().evaluate(_txn(3, 20, "IN"), history) is False


def test_empty_history_not_flagged():
    assert CountryHopRule().evaluate(_txn(1, 0, "IN"), []) is False


def test_rejects_bad_window():
    with pytest.raises(ValueError):
        CountryHopRule(window=timedelta(0))
