import pytest

from src.evaluation.metrics import evaluate, precision_recall
from src.rules.base import Flag
from tests.helpers import make_txn


def test_precision_recall_basic():
    precision, recall = precision_recall({"a", "b", "c", "d"}, {"a", "b", "x"})
    assert precision == pytest.approx(0.5)
    assert recall == pytest.approx(2 / 3)


def test_empty_sets_give_zero_not_an_error():
    assert precision_recall(set(), {"a"}) == (0.0, 0.0)
    assert precision_recall({"a"}, set()) == (0.0, 0.0)


def test_evaluate_scores_each_rule_against_its_own_pattern():
    txns = [
        make_txn("T1", fraud_pattern="velocity"),
        make_txn("T2", fraud_pattern="velocity"),
        make_txn("T3"),
        make_txn("T4", fraud_pattern="geo_mismatch"),
    ]
    flags = [Flag("T1", "velocity"), Flag("T3", "velocity"), Flag("T4", "geo_mismatch")]
    result = evaluate(txns, flags)

    assert result["velocity"].precision == pytest.approx(0.5)
    assert result["velocity"].recall == pytest.approx(0.5)
    assert result["geo_mismatch"].precision == 1.0
    assert result["geo_mismatch"].recall == 1.0
    assert result["overall"].flagged == 3
    assert result["overall"].positives == 3


def test_rule_that_never_fires_has_zero_recall():
    txns = [make_txn("T1", fraud_pattern="amount_spike")]
    result = evaluate(txns, [])
    assert result["amount_spike"].recall == 0.0
