from datetime import datetime, timedelta

import pytest

from src.generator import Transaction
from src.rules import RapidSuccessionRule, Rule

T0 = datetime(2026, 3, 9, 14, 0, 0)


def _txn(tid: str, ts: datetime) -> Transaction:
    return Transaction(tid, "ACC0001", ts, 20.0, "grocery", "IN")


def test_implements_interface():
    assert isinstance(RapidSuccessionRule(), Rule)
    assert RapidSuccessionRule().name == "rapid_succession"


def test_flags_close_follow_up():
    rule = RapidSuccessionRule()
    assert rule.evaluate(_txn("T2", T0 + timedelta(seconds=3)), [_txn("T1", T0)]) is True


def test_exactly_at_max_gap_flagged():
    rule = RapidSuccessionRule()
    assert rule.evaluate(_txn("T2", T0 + timedelta(seconds=10)), [_txn("T1", T0)]) is True


def test_slow_follow_up_not_flagged():
    rule = RapidSuccessionRule()
    assert rule.evaluate(_txn("T2", T0 + timedelta(seconds=11)), [_txn("T1", T0)]) is False


def test_no_history_not_flagged():
    assert RapidSuccessionRule().evaluate(_txn("T1", T0), []) is False


def test_out_of_order_not_flagged():
    rule = RapidSuccessionRule()
    assert rule.evaluate(_txn("T2", T0 - timedelta(seconds=2)), [_txn("T1", T0)]) is False


def test_invalid_max_gap():
    with pytest.raises(ValueError):
        RapidSuccessionRule(max_gap=timedelta(0))
