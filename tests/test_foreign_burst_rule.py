from datetime import datetime, timedelta

import pytest

from src.generator import Transaction
from src.rules import ForeignBurstRule, Rule

NOW = datetime(2026, 3, 14, 14, 0)


def _txn(country: str, ts: datetime) -> Transaction:
    return Transaction("T1", "ACC0001", ts, 50.0, "grocery", country)


HOME = [_txn("IN", NOW - timedelta(days=3, minutes=i)) for i in range(8)]
ABROAD = [_txn("US", NOW - timedelta(minutes=m)) for m in (10, 30)]


def test_implements_interface():
    assert isinstance(ForeignBurstRule(), Rule)
    assert ForeignBurstRule().name == "foreign_burst"


def test_flags_third_purchase_abroad_in_window():
    assert ForeignBurstRule().evaluate(_txn("US", NOW), HOME + ABROAD) is True


def test_ignores_home_country_and_short_bursts():
    rule = ForeignBurstRule()
    assert rule.evaluate(_txn("IN", NOW), HOME + ABROAD) is False
    assert rule.evaluate(_txn("US", NOW), HOME + ABROAD[:1]) is False


def test_ignores_old_foreign_purchases():
    old = [_txn("US", NOW - timedelta(minutes=m)) for m in (90, 120)]
    assert ForeignBurstRule().evaluate(_txn("US", NOW), HOME + old) is False
    assert ForeignBurstRule(window_minutes=180).evaluate(_txn("US", NOW), HOME + old) is True


def test_needs_min_history():
    assert ForeignBurstRule().evaluate(_txn("US", NOW), ABROAD) is False


def test_invalid_parameters():
    with pytest.raises(ValueError):
        ForeignBurstRule(min_count=1)
    with pytest.raises(ValueError):
        ForeignBurstRule(window_minutes=0)
    with pytest.raises(ValueError):
        ForeignBurstRule(min_history=0)
