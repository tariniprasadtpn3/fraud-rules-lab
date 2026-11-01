from datetime import datetime

import pytest

from src.generator import Transaction
from src.rules import ForeignNightRule, Rule


def _txn(hour: int, country: str) -> Transaction:
    return Transaction("T1", "ACC0001", datetime(2026, 3, 9, hour, 0), 50.0, "grocery", country)


HISTORY = [_txn(14, "IN") for _ in range(6)]


def test_implements_interface():
    assert isinstance(ForeignNightRule(), Rule)
    assert ForeignNightRule().name == "foreign_night"


def test_flags_foreign_purchase_at_night():
    assert ForeignNightRule().evaluate(_txn(3, "US"), HISTORY) is True


def test_foreign_purchase_by_day_not_flagged():
    assert ForeignNightRule().evaluate(_txn(14, "US"), HISTORY) is False


def test_home_purchase_at_night_not_flagged():
    assert ForeignNightRule().evaluate(_txn(3, "IN"), HISTORY) is False


def test_window_end_is_exclusive():
    assert ForeignNightRule().evaluate(_txn(5, "US"), HISTORY) is False


def test_window_wrapping_midnight():
    rule = ForeignNightRule(start_hour=23, end_hour=4)
    assert rule.evaluate(_txn(23, "US"), HISTORY) is True
    assert rule.evaluate(_txn(2, "US"), HISTORY) is True
    assert rule.evaluate(_txn(12, "US"), HISTORY) is False


def test_short_history_not_flagged():
    assert ForeignNightRule().evaluate(_txn(3, "US"), HISTORY[:4]) is False


def test_invalid_parameters_rejected():
    with pytest.raises(ValueError):
        ForeignNightRule(start_hour=24)
    with pytest.raises(ValueError):
        ForeignNightRule(start_hour=3, end_hour=3)
    with pytest.raises(ValueError):
        ForeignNightRule(min_history=0)
