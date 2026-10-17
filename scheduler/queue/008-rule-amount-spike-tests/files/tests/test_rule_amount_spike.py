from src.rules.amount_spike import AmountSpikeRule
from tests.helpers import make_txn


def steady_history(mean=100.0, n=6):
    return [make_txn(f"H{i}", days=-(i + 1), amount=mean) for i in range(n)]


def test_flags_a_large_spike():
    rule = AmountSpikeRule(multiplier=5.0, min_history=5)
    assert rule.evaluate(make_txn("NOW", amount=600.0), steady_history())


def test_normal_amount_is_not_flagged():
    rule = AmountSpikeRule(multiplier=5.0, min_history=5)
    assert not rule.evaluate(make_txn("NOW", amount=120.0), steady_history())


def test_exactly_at_the_multiplier_is_not_flagged():
    rule = AmountSpikeRule(multiplier=5.0, min_history=5)
    assert not rule.evaluate(make_txn("NOW", amount=500.0), steady_history())


def test_needs_minimum_history():
    rule = AmountSpikeRule(multiplier=5.0, min_history=5)
    assert not rule.evaluate(make_txn("NOW", amount=600.0), steady_history(n=3))


def test_old_history_outside_the_window_is_ignored():
    rule = AmountSpikeRule(multiplier=5.0, min_history=5)
    old = [make_txn(f"H{i}", days=-(100 + i), amount=100.0) for i in range(6)]
    assert not rule.evaluate(make_txn("NOW", amount=600.0), old)
