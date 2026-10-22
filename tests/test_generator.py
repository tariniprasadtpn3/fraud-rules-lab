from datetime import timedelta

import pytest

from src.generator import (
    AMOUNT_SPIKE,
    COUNTRIES,
    DORMANT_REACTIVATION,
    GEO_MISMATCH,
    PATTERNS,
    VELOCITY,
    generate_transactions,
    write_csv,
)


def _by_account(txns):
    grouped = {}
    for t in txns:
        grouped.setdefault(t.account_id, []).append(t)
    return grouped


def test_same_seed_gives_identical_output():
    assert generate_transactions(seed=7) == generate_transactions(seed=7)


def test_different_seed_gives_different_output():
    assert generate_transactions(seed=1) != generate_transactions(seed=2)


def test_output_is_time_ordered_with_unique_ids():
    txns = generate_transactions()
    assert [t.timestamp for t in txns] == sorted(t.timestamp for t in txns)
    assert len({t.txn_id for t in txns}) == len(txns)


def test_labels_are_consistent():
    for t in generate_transactions():
        assert t.is_fraud == (t.fraud_pattern is not None)
        if t.fraud_pattern is not None:
            assert t.fraud_pattern in PATTERNS


def test_every_pattern_is_injected_by_default():
    seen = {t.fraud_pattern for t in generate_transactions() if t.is_fraud}
    assert seen == set(PATTERNS)


def test_velocity_burst_is_tight():
    grouped = _by_account(generate_transactions())
    bursts = 0
    for txns in grouped.values():
        fraud = [t for t in txns if t.fraud_pattern == VELOCITY]
        if fraud:
            bursts += 1
            assert len(fraud) == 6
            span = max(t.timestamp for t in fraud) - min(t.timestamp for t in fraud)
            assert span <= timedelta(minutes=4)
    assert bursts > 0


def test_amount_spike_exceeds_normal_range():
    grouped = _by_account(generate_transactions())
    checked = 0
    for txns in grouped.values():
        spikes = [t for t in txns if t.fraud_pattern == AMOUNT_SPIKE]
        if spikes:
            checked += 1
            normal_max = max(t.amount for t in txns if not t.is_fraud)
            assert spikes[0].amount > normal_max
    assert checked > 0


def test_geo_mismatch_uses_foreign_country():
    grouped = _by_account(generate_transactions())
    checked = 0
    for txns in grouped.values():
        fraud = [t for t in txns if t.fraud_pattern == GEO_MISMATCH]
        if fraud:
            checked += 1
            home = {t.country for t in txns if not t.is_fraud}
            assert len(home) == 1
            assert fraud[0].country in COUNTRIES
            assert fraud[0].country not in home
    assert checked > 0


def test_dormant_account_reactivates_after_long_gap():
    grouped = _by_account(generate_transactions(days=30))
    checked = 0
    for txns in grouped.values():
        fraud = [t for t in txns if t.fraud_pattern == DORMANT_REACTIVATION]
        if fraud:
            checked += 1
            last_normal = max(t.timestamp for t in txns if not t.is_fraud)
            assert fraud[0].timestamp - last_normal > timedelta(days=15)
    assert checked > 0


@pytest.mark.parametrize(
    "kwargs",
    [{"n_accounts": 0}, {"days": 3}, {"fraud_account_ratio": 1.5}],
)
def test_invalid_arguments_raise(kwargs):
    with pytest.raises(ValueError):
        generate_transactions(**kwargs)


def test_write_csv_round_trip(tmp_path):
    txns = generate_transactions(n_accounts=5, days=10)
    out = tmp_path / "nested" / "transactions.csv"
    write_csv(txns, out)
    lines = out.read_text().splitlines()
    assert lines[0].startswith("txn_id,account_id,timestamp")
    assert len(lines) == len(txns) + 1


def test_new_patterns_are_injected_with_expected_shape():
    from src.generator import RARE_CATEGORY

    txns = generate_transactions(n_accounts=100, days=30, fraud_account_ratio=0.5, seed=3)
    by_pattern = {}
    for t in txns:
        if t.is_fraud:
            by_pattern.setdefault(t.fraud_pattern, []).append(t)
    assert {"repeat_amount", "country_hop", "round_amount", "new_category"} <= set(by_pattern)
    assert all(t.amount % 500 == 0 and t.amount >= 1500 for t in by_pattern["round_amount"])
    assert all(t.merchant_category == RARE_CATEGORY for t in by_pattern["new_category"])
    assert not any(t.merchant_category == RARE_CATEGORY for t in txns if not t.is_fraud)
