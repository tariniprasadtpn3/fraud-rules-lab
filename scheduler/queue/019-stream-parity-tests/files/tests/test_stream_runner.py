from datetime import timedelta

from src.batch.runner import run_batch
from src.generator.fraud import inject_fraud
from src.generator.synthetic import generate_transactions
from src.rules.base import Flag
from src.rules.registry import default_rules
from src.rules.velocity import VelocityRule
from src.stream.runner import StreamProcessor, run_stream
from tests.helpers import make_txn


def test_processor_flags_a_burst_incrementally():
    processor = StreamProcessor([VelocityRule(max_txns=4)])
    results = [processor.process(make_txn(f"T{i}", minutes=i)) for i in range(6)]
    assert [bool(r) for r in results] == [False, False, False, False, True, True]
    assert results[4] == [Flag("T4", "velocity")]


def test_state_stays_bounded_for_a_long_running_account():
    processor = StreamProcessor(default_rules())
    retention = processor.retention
    for day in range(400):
        processor.process(make_txn(f"T{day}", days=day))
    assert processor.state_size("A1") <= retention.days + 2


def test_latest_transaction_is_always_kept():
    processor = StreamProcessor([VelocityRule(window=timedelta(minutes=1))])
    processor.process(make_txn("T0", days=0))
    processor.process(make_txn("T1", days=365))
    assert processor.state_size("A1") >= 1


def test_stream_matches_batch_on_synthetic_data():
    txns = inject_fraud(generate_transactions(n_accounts=25, days=150, seed=5))
    batch = run_batch(txns, default_rules())
    stream = run_stream(txns, default_rules())
    assert len(batch) == len(stream)
    assert set(batch) == set(stream)
    assert batch  # the data really does trigger rules
