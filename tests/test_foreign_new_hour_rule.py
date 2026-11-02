from datetime import datetime

import pytest

from src.generator import Transaction
from src.rules import ForeignNewHourRule, Rule


def _txn(hour: int, country: str) -> Transaction:
    return Transaction("T1", "ACC0001", datetime(2026, 3, 9, hour, 0), 50.0, "grocery", country)


HISTORY = [_txn(14, "IN") for _ in range(10)]


def test_implements_interface():
    assert isinstance(ForeignNewHourRule(), Rule)
    assert ForeignNewHourRule().name == "foreign_new_hour"


def test_flags_new_hour_abroad():
    assert ForeignNewHourRule().evaluate(_txn(3, "US"), HISTORY) is True


def test_ignores_known_hour_or_home_country():
    rule = ForeignNewHourRule()
    assert rule.evaluate(_txn(14, "US"), HISTORY) is False
    assert rule.evaluate(_txn(3, "IN"), HISTORY) is False


def test_needs_min_history():
    assert ForeignNewHourRule().evaluate(_txn(3, "US"), HISTORY[:9]) is False
    assert ForeignNewHourRule(min_history=2).evaluate(_txn(3, "US"), HISTORY[:2]) is True


def test_invalid_parameters():
    with pytest.raises(ValueError):
        ForeignNewHourRule(min_history=0)
