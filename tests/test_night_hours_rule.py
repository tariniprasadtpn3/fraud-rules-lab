from datetime import datetime

import pytest

from src.generator import Transaction
from src.rules import NightHoursRule, Rule


def _txn(hour: int, minute: int = 0) -> Transaction:
    return Transaction("T1", "ACC0001", datetime(2026, 3, 1, hour, minute), 25.0, "grocery", "IN")


def test_implements_interface():
    assert isinstance(NightHoursRule(), Rule)
    assert NightHoursRule().name == "night_hours"


def test_flags_inside_window_and_ignores_history():
    assert NightHoursRule().evaluate(_txn(3), []) is True


def test_window_start_inclusive_end_exclusive():
    rule = NightHoursRule(start_hour=1, end_hour=5)
    assert rule.evaluate(_txn(1, 0), []) is True
    assert rule.evaluate(_txn(4, 59), []) is True
    assert rule.evaluate(_txn(5, 0), []) is False
    assert rule.evaluate(_txn(0, 59), []) is False


def test_daytime_not_flagged():
    assert NightHoursRule().evaluate(_txn(14), []) is False


def test_window_wrapping_midnight():
    rule = NightHoursRule(start_hour=23, end_hour=5)
    assert rule.evaluate(_txn(23), []) is True
    assert rule.evaluate(_txn(0), []) is True
    assert rule.evaluate(_txn(4), []) is True
    assert rule.evaluate(_txn(5), []) is False
    assert rule.evaluate(_txn(12), []) is False


@pytest.mark.parametrize("start,end", [(-1, 5), (1, 24), (3, 3)])
def test_rejects_bad_hours(start, end):
    with pytest.raises(ValueError):
        NightHoursRule(start_hour=start, end_hour=end)
