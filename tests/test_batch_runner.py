import csv
from datetime import datetime, timedelta

from src.batch import FlaggedTransaction, default_rules, run_batch, write_flagged_csv
from src.generator import generate_transactions, Transaction
from src.rules import VelocityRule

T0 = datetime(2026, 3, 1, 12, 0, 0)


def _txn(seconds: int, i: int, acc: str = "ACC0001") -> Transaction:
    return Transaction(f"T{i}", acc, T0 + timedelta(seconds=seconds), 100.0, "dining", "IN")


def test_default_rules_cover_all_four_rules():
    assert {r.name for r in default_rules()} == {
        "velocity", "amount_spike", "geo_mismatch", "dormant_reactivation",
    }


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
