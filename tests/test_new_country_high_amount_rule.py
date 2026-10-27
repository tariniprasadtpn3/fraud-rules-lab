from datetime import datetime, timedelta

import pytest

from src.generator import Transaction
from src.rules import NewCountryHighAmountRule, Rule


def _txn(i: int, amount: float = 50.0, country: str = "IN") -> Transaction:
    ts = datetime(2026, 3, 1, 12, 0) + timedelta(days=i)
    return Transaction(f"T{i}", "ACC0001", ts, amount, "grocery", country)


def _history(n: int = 6):
    return [_txn(i) for i in range(n)]


def test_implements_interface():
    assert isinstance(NewCountryHighAmountRule(), Rule)
    assert NewCountryHighAmountRule().name == "new_country_high_amount"


def test_flags_large_amount_in_new_country():
    assert NewCountryHighAmountRule().evaluate(_txn(9, 400.0, "BR"), _history()) is True


def test_amount_at_threshold_flagged():
    assert NewCountryHighAmountRule().evaluate(_txn(9, 300.0, "BR"), _history()) is True


def test_small_amount_in_new_country_not_flagged():
    assert NewCountryHighAmountRule().evaluate(_txn(9, 299.0, "BR"), _history()) is False


def test_large_amount_in_known_country_not_flagged():
    assert NewCountryHighAmountRule().evaluate(_txn(9, 900.0, "IN"), _history()) is False


def test_previously_visited_country_not_flagged():
    hist = _history() + [_txn(7, 20.0, "BR")]
    assert NewCountryHighAmountRule().evaluate(_txn(9, 900.0, "BR"), hist) is False


def test_too_little_history():
    assert NewCountryHighAmountRule().evaluate(_txn(9, 900.0, "BR"), _history(4)) is False


def test_invalid_parameters():
    with pytest.raises(ValueError):
        NewCountryHighAmountRule(threshold=0)
    with pytest.raises(ValueError):
        NewCountryHighAmountRule(min_history=0)
