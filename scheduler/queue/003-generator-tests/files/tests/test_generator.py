from src.generator.synthetic import generate_transactions


def test_same_seed_is_reproducible():
    a = generate_transactions(n_accounts=10, days=30, seed=1)
    b = generate_transactions(n_accounts=10, days=30, seed=1)
    assert a == b


def test_different_seed_gives_different_data():
    a = generate_transactions(n_accounts=10, days=30, seed=1)
    b = generate_transactions(n_accounts=10, days=30, seed=2)
    assert a != b


def test_sorted_by_time_then_id():
    txns = generate_transactions(n_accounts=10, days=30, seed=1)
    keys = [(t.timestamp, t.txn_id) for t in txns]
    assert keys == sorted(keys)


def test_ids_are_unique():
    txns = generate_transactions(n_accounts=10, days=30, seed=1)
    assert len({t.txn_id for t in txns}) == len(txns)


def test_clean_data_has_positive_amounts_and_no_labels():
    txns = generate_transactions(n_accounts=10, days=30, seed=1)
    assert txns
    assert all(t.amount > 0 for t in txns)
    assert not any(t.is_fraud for t in txns)


def test_accounts_transact_only_at_home():
    txns = generate_transactions(n_accounts=10, days=30, seed=1)
    assert all(t.country == t.home_country for t in txns)
