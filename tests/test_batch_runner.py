import csv
from datetime import datetime, timedelta

from src.batch import FlaggedTransaction, core_rules, default_rules, run_batch, write_flagged_csv
from src.generator import generate_transactions, Transaction
from src.rules import VelocityRule

T0 = datetime(2026, 3, 1, 12, 0, 0)


def _txn(seconds: int, i: int, acc: str = "ACC0001") -> Transaction:
    return Transaction(f"T{i}", acc, T0 + timedelta(seconds=seconds), 100.0, "dining", "IN")


CORE = {"velocity", "amount_spike", "geo_mismatch", "dormant_reactivation"}
EXTRA = {"high_amount", "night_hours", "round_amount", "new_category", "repeat_amount", "country_hop"}


def test_core_rules_are_the_four_original_rules():
    assert {r.name for r in core_rules()} == CORE


def test_default_rules_include_core_and_extra_rules():
    names = [r.name for r in default_rules()]
    assert set(names) == CORE | EXTRA
    assert len(names) == len(set(names))


def test_flags_velocity_burst_and_reports_rule_name():
    txns = [_txn(0, 1), _txn(60, 2), _txn(120, 3)]
    flagged = run_batch(txns, [VelocityRule()])
    assert [f.txn.txn_id for f in flagged] == ["T3"]
    assert flagged[0].rules == ("velocity",)


def test_accounts_are_isolated_and_input_order_does_not_matter():
    txns = [_txn(120, 3), _txn(0, 1), _txn(60, 2, acc="ACC0002")]
    assert run_batch(txns, [VelocityRule()]) == []


def test_generated_data_is_flagged_and_deterministic():
    txns = generate_transactions(seed=7)
    first = run_batch(txns)
    assert first and all(isinstance(f, FlaggedTransaction) for f in first)
    assert first == run_batch(generate_transactions(seed=7))
    assert len(first) < len(txns)


def test_write_flagged_csv(tmp_path):
    flagged = run_batch([_txn(0, 1), _txn(60, 2), _txn(120, 3)], [VelocityRule()])
    out = tmp_path / "flagged.csv"
    write_flagged_csv(flagged, out)
    rows = list(csv.DictReader(out.open()))
    assert rows[0]["txn_id"] == "T3" and rows[0]["rules"] == "velocity"


def test_min_rules_requires_several_rules_to_agree():
    from src.rules import HighAmountRule, RoundAmountRule

    txns = [
        Transaction("T1", "ACC0001", T0, 6000.0, "dining", "IN"),  # high + round
        Transaction("T2", "ACC0002", T0, 6001.0, "dining", "IN"),  # high only
    ]
    rules = [HighAmountRule(), RoundAmountRule()]
    assert [f.txn.txn_id for f in run_batch(txns, rules)] == ["T1", "T2"]
    both = run_batch(txns, rules, min_rules=2)
    assert [f.txn.txn_id for f in both] == ["T1"]
    assert both[0].rules == ("high_amount", "round_amount")


def test_min_rules_rejects_zero():
    import pytest

    with pytest.raises(ValueError):
        run_batch([], min_rules=0)


def test_min_rules_raises_precision_on_generated_data():
    from src.evaluation import evaluate

    txns = generate_transactions(seed=42)
    loose = evaluate(txns, run_batch(txns))["overall"]
    strict = evaluate(txns, run_batch(txns, min_rules=2))["overall"]
    assert strict.precision >= loose.precision
    assert strict.tp + strict.fp < loose.tp + loose.fp
