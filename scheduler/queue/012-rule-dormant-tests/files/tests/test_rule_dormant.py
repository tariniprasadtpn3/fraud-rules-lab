from src.rules.dormant import DormantReactivationRule
from tests.helpers import make_txn


def test_flags_large_transaction_after_long_gap():
    rule = DormantReactivationRule(dormant_days=90, min_amount=100.0)
    history = [make_txn("H1", days=-120)]
    assert rule.evaluate(make_txn("NOW", amount=300.0), history)


def test_active_account_is_not_flagged():
    rule = DormantReactivationRule(dormant_days=90, min_amount=100.0)
    history = [make_txn("H1", days=-2)]
    assert not rule.evaluate(make_txn("NOW", amount=300.0), history)


def test_small_amount_is_not_flagged():
    rule = DormantReactivationRule(dormant_days=90, min_amount=100.0)
    history = [make_txn("H1", days=-120)]
    assert not rule.evaluate(make_txn("NOW", amount=20.0), history)


def test_new_account_is_not_dormant():
    rule = DormantReactivationRule(dormant_days=90, min_amount=100.0)
    assert not rule.evaluate(make_txn("NOW", amount=300.0), [])


def test_boundary_is_inclusive():
    rule = DormantReactivationRule(dormant_days=90, min_amount=100.0)
    assert rule.evaluate(make_txn("NOW", amount=300.0), [make_txn("H1", days=-90)])
    assert not rule.evaluate(make_txn("NOW", amount=300.0), [make_txn("H1", days=-89)])
