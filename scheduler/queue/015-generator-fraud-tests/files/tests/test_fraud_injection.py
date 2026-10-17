from src.generator.fraud import BURST_SIZE, PATTERNS, inject_fraud
from src.generator.synthetic import generate_transactions


def make_base():
    return generate_transactions(n_accounts=30, days=120, seed=3)


def test_every_pattern_is_injected():
    result = inject_fraud(make_base())
    patterns = {t.fraud_pattern for t in result if t.is_fraud}
    assert patterns == set(PATTERNS)


def test_velocity_bursts_have_the_expected_size():
    result = inject_fraud(make_base(), per_pattern=5)
    bursts = [t for t in result if t.fraud_pattern == "velocity"]
    assert len(bursts) == 5 * BURST_SIZE


def test_original_transactions_are_preserved_and_unlabelled():
    base = make_base()
    result = inject_fraud(base)
    by_id = {t.txn_id: t for t in result}
    assert all(by_id[t.txn_id] == t and not t.is_fraud for t in base)


def test_input_list_is_not_modified():
    base = make_base()
    size = len(base)
    inject_fraud(base)
    assert len(base) == size


def test_injection_is_reproducible():
    assert inject_fraud(make_base(), seed=1) == inject_fraud(make_base(), seed=1)


def test_result_is_sorted_with_unique_ids():
    result = inject_fraud(make_base())
    keys = [(t.timestamp, t.txn_id) for t in result]
    assert keys == sorted(keys)
    assert len({t.txn_id for t in result}) == len(result)
