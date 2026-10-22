"""Edge cases across the generator, runners and evaluation."""

from datetime import datetime, timedelta

import pytest

from src.batch import run_batch
from src.evaluation import Metrics, evaluate
from src.generator import PATTERNS, Transaction, generate_transactions
from src.rules import (
    CountryHopRule,
    HighAmountRule,
    NightHoursRule,
    RepeatAmountRule,
    VelocityRule,
)
from src.stream import StreamProcessor, run_stream

T0 = datetime(2026, 3, 1, 12, 0, 0)


def _txn(i: int, seconds: int = 0, amount: float = 100.0, country: str = "IN", acc: str = "ACC0001"):
    return Transaction(f"T{i}", acc, T0 + timedelta(seconds=seconds), amount, "dining", country)


def test_batch_and_stream_handle_empty_input():
    assert run_batch([]) == []
    assert list(run_stream([])) == []


def test_zero_fraud_ratio_has_no_fraud_and_full_ratio_is_valid():
    assert not any(t.is_fraud for t in generate_transactions(fraud_account_ratio=0.0, seed=1))
    assert any(t.is_fraud for t in generate_transactions(n_accounts=len(PATTERNS), fraud_account_ratio=1.0, seed=1))


@pytest.mark.parametrize("kwargs", [{"n_accounts": 0}, {"days": 5}, {"fraud_account_ratio": 1.5}, {"fraud_account_ratio": -0.1}])
def test_generator_rejects_bad_arguments(kwargs):
    with pytest.raises(ValueError):
        generate_transactions(**kwargs)


def test_generator_ids_unique_and_sorted():
    txns = generate_transactions(seed=5)
    assert len({t.txn_id for t in txns}) == len(txns)
    assert [t.timestamp for t in txns] == sorted(t.timestamp for t in txns)


def test_evaluation_with_nothing_flagged_or_no_fraud():
    txns = [_txn(1), _txn(2, 60)]
    metrics = evaluate(txns, [])["overall"]
    assert metrics == Metrics(tp=0, fp=0, fn=0)
    assert metrics.precision == metrics.recall == metrics.f1 == 0.0


def test_evaluation_counts_false_positive_when_no_fraud_exists():
    txns = [_txn(1, amount=9000.0)]
    result = evaluate(txns, run_batch(txns, [HighAmountRule()]))
    assert result["overall"] == Metrics(tp=0, fp=1, fn=0)
    assert result["high_amount"].precision == 0.0


def test_identical_timestamps_are_ordered_by_txn_id():
    txns = [_txn(3), _txn(1), _txn(2)]
    flagged = run_batch(txns, [VelocityRule()])
    assert [f.txn.txn_id for f in flagged] == ["T3"]


def test_velocity_ignores_other_accounts_with_same_timestamp():
    txns = [_txn(1, acc="A"), _txn(2, acc="B"), _txn(3, acc="C")]
    assert run_batch(txns, [VelocityRule()]) == []


def test_stream_max_history_bounds_memory_but_keeps_recent_context():
    processor = StreamProcessor([RepeatAmountRule()], max_history=1)
    assert processor.process(_txn(1, 0, 50.0)) is None
    assert processor.process(_txn(2, 60, 70.0)) is None
    # Only the latest transaction (70.0) is remembered, so 50.0 is no longer a repeat.
    assert processor.process(_txn(3, 120, 50.0)) is None
    assert processor.process(_txn(4, 180, 50.0)) is not None


def test_country_hop_ignores_out_of_order_history():
    rule = CountryHopRule()
    # A "previous" transaction timestamped after the current one is not a hop.
    assert rule.evaluate(_txn(2, 0, country="US"), [_txn(1, 60, country="IN")]) is False


def test_night_hours_wraparound_edges():
    rule = NightHoursRule(start_hour=23, end_hour=5)
    at = lambda h: Transaction("T", "A", datetime(2026, 3, 1, h, 59), 1.0, "dining", "IN")
    assert [rule.evaluate(at(h), []) for h in (22, 23, 0, 4, 5)] == [False, True, True, True, False]


def test_high_amount_is_strictly_above_threshold():
    rule = HighAmountRule(threshold=100.0)
    assert rule.evaluate(_txn(1, amount=100.0), []) is False
    assert rule.evaluate(_txn(2, amount=100.01), []) is True
