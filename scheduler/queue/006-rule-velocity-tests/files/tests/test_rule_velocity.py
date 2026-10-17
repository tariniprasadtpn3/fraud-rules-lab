from datetime import timedelta

from src.rules.velocity import VelocityRule
from tests.helpers import make_txn


def burst(n):
    return [make_txn(f"H{i}", minutes=i) for i in range(n)]


def test_flags_when_threshold_is_exceeded():
    rule = VelocityRule(max_txns=5, window=timedelta(minutes=10))
    assert rule.evaluate(make_txn("NOW", minutes=5), burst(5))


def test_does_not_flag_at_the_threshold():
    rule = VelocityRule(max_txns=5, window=timedelta(minutes=10))
    assert not rule.evaluate(make_txn("NOW", minutes=4), burst(4))


def test_transactions_outside_the_window_are_ignored():
    rule = VelocityRule(max_txns=5, window=timedelta(minutes=10))
    old = [make_txn(f"H{i}", minutes=-120 + i) for i in range(10)]
    assert not rule.evaluate(make_txn("NOW", minutes=0), old)


def test_empty_history_is_not_flagged():
    assert not VelocityRule().evaluate(make_txn("NOW"), [])


def test_lookback_matches_the_window():
    window = timedelta(minutes=3)
    assert VelocityRule(window=window).lookback == window
