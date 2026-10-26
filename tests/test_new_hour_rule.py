from datetime import datetime, timedelta

import pytest

from src.generator import Transaction
from src.rules import NewHourRule, Rule

T0 = datetime(2026, 3, 9, 12, 0, 0)


def _txn(i: int, hour: int) -> Transaction:
    ts = datetime(2026, 3, 1, hour, 30) + timedelta(days=i)
    return Transaction(f"T{i}", "ACC0001", ts, 20.0, "grocery", "IN")


def _history(n: int = 10, hour: int = 12):
    return [_txn(i, hour) for i in range(n)]


def test_implements_interface():
    assert isinstance(NewHourRule(), Rule)
    assert NewHourRule().name == "new_hour"


def test_flags_unseen_hour():
    assert NewHourRule().evaluate(_txn(20, 3), _history()) is True


def test_seen_hour_not_flagged():
    assert NewHourRule().evaluate(_txn(20, 12), _history()) is False


def test_short_history_not_flagged():
    assert NewHourRule().evaluate(_txn(20, 3), _history(9)) is False


def test_min_history_boundary():
    assert NewHourRule(min_history=3).evaluate(_txn(20, 3), _history(3)) is True


def test_invalid_min_history():
    with pytest.raises(ValueError):
        NewHourRule(min_history=0)
