from datetime import datetime, timedelta

import pytest

from src.generator import Transaction
from src.rules import NewCountryRule, Rule

T0 = datetime(2026, 3, 1, 12, 0)


def _txn(i: int, country: str) -> Transaction:
    return Transaction(f"T{i}", "ACC0001", T0 + timedelta(hours=i), 40.0, "grocery", country)


def _hist(countries):
    return [_txn(i, c) for i, c in enumerate(countries)]


def test_implements_interface():
    assert isinstance(NewCountryRule(), Rule)
    assert NewCountryRule().name == "new_country"


def test_flags_never_seen_country():
    assert NewCountryRule().evaluate(_txn(9, "US"), _hist(["IN"] * 5)) is True


def test_known_country_not_flagged():
    assert NewCountryRule().evaluate(_txn(9, "IN"), _hist(["IN"] * 5)) is False


def test_second_visit_to_foreign_country_not_flagged():
    hist = _hist(["IN", "IN", "IN", "IN", "US", "IN"])
    assert NewCountryRule().evaluate(_txn(9, "US"), hist) is False


def test_short_history_not_flagged():
    assert NewCountryRule().evaluate(_txn(9, "US"), _hist(["IN"] * 4)) is False


def test_invalid_parameters():
    with pytest.raises(ValueError):
        NewCountryRule(min_history=0)
