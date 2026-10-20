from datetime import datetime

import pytest

from src.batch import FlaggedTransaction, run_batch
from src.evaluation import Metrics, evaluate
from src.generator import Transaction, generate_transactions

T0 = datetime(2026, 3, 1)


def _t(i, fraud=False, pattern=None):
    return Transaction(f"T{i}", "ACC1", T0, 10.0, "dining", "IN", fraud, pattern)


def test_metrics_math():
    m = Metrics(tp=3, fp=1, fn=3)
    assert m.precision == 0.75
    assert m.recall == 0.5
    assert m.f1 == pytest.approx(0.6)


def test_zero_division_is_safe():
    m = Metrics(0, 0, 0)
    assert (m.precision, m.recall, m.f1) == (0.0, 0.0, 0.0)


def test_overall_and_per_rule_counts():
    txns = [_t(1, True, "velocity"), _t(2, True, "velocity"), _t(3), _t(4, True, "geo_mismatch")]
    flagged = [
        FlaggedTransaction(txns[0], ("velocity",)),
        FlaggedTransaction(txns[2], ("velocity",)),
        FlaggedTransaction(txns[3], ("geo_mismatch",)),
    ]
    res = evaluate(txns, flagged)
    assert res["overall"] == Metrics(tp=2, fp=1, fn=1)
    assert res["velocity"] == Metrics(tp=1, fp=1, fn=1)
    assert res["geo_mismatch"] == Metrics(tp=1, fp=0, fn=0)


def test_end_to_end_on_generated_data_has_some_recall():
    txns = generate_transactions()
    res = evaluate(txns, run_batch(txns))
    assert 0.0 < res["overall"].recall <= 1.0
    assert 0.0 <= res["overall"].precision <= 1.0
