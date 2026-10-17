from src.rules.geo_mismatch import GeoMismatchRule
from tests.helpers import make_txn


def home_history():
    return [make_txn(f"H{i}", days=-(i + 1)) for i in range(5)]


def test_flags_first_large_foreign_transaction():
    rule = GeoMismatchRule(min_amount=100.0)
    txn = make_txn("NOW", country="US", amount=250.0)
    assert rule.evaluate(txn, home_history())


def test_home_country_is_never_flagged():
    rule = GeoMismatchRule(min_amount=100.0)
    assert not rule.evaluate(make_txn("NOW", amount=900.0), home_history())


def test_small_foreign_amount_is_not_flagged():
    rule = GeoMismatchRule(min_amount=100.0)
    txn = make_txn("NOW", country="US", amount=40.0)
    assert not rule.evaluate(txn, home_history())


def test_repeat_foreign_country_is_not_flagged():
    rule = GeoMismatchRule(min_amount=100.0)
    history = home_history() + [make_txn("US1", days=-2, country="US", amount=30.0)]
    txn = make_txn("NOW", country="US", amount=250.0)
    assert not rule.evaluate(txn, history)


def test_stale_foreign_history_is_ignored():
    rule = GeoMismatchRule(min_amount=100.0)
    history = home_history() + [make_txn("US1", days=-60, country="US", amount=30.0)]
    txn = make_txn("NOW", country="US", amount=250.0)
    assert rule.evaluate(txn, history)
