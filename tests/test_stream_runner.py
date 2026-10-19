from datetime import datetime, timedelta

from src.batch import run_batch
from src.generator import Transaction, generate_transactions
from src.rules import VelocityRule
from src.stream import StreamProcessor, run_stream

T0 = datetime(2026, 3, 1, 12, 0, 0)


def _txn(seconds: int, i: int, acc: str = "ACC0001") -> Transaction:
    return Transaction(f"T{i}", acc, T0 + timedelta(seconds=seconds), 100.0, "dining", "IN")


def test_process_returns_verdict_per_transaction():
    p = StreamProcessor([VelocityRule()])
    assert p.process(_txn(0, 1)) is None
    assert p.process(_txn(60, 2)) is None
    result = p.process(_txn(120, 3))
    assert result is not None and result.rules == ("velocity",)


def test_accounts_are_isolated():
    p = StreamProcessor([VelocityRule()])
    results = [p.process(_txn(0, 1)), p.process(_txn(60, 2, "ACC0002")), p.process(_txn(120, 3))]
    assert results == [None, None, None]


def test_max_history_bounds_memory():
    p = StreamProcessor([VelocityRule()], max_history=2)
    for i in range(10):
        p.process(_txn(i * 3600, i))
    assert len(p._history["ACC0001"]) == 2


def test_stream_matches_batch_on_generated_data():
    txns = sorted(generate_transactions(seed=7), key=lambda t: (t.timestamp, t.txn_id))
    streamed = list(run_stream(iter(txns)))
    assert streamed and streamed == run_batch(txns)
