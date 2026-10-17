import random

from src.batch.runner import run_batch
from src.rules.base import Flag
from src.rules.registry import default_rules
from src.rules.velocity import VelocityRule
from tests.helpers import make_txn


def test_flags_a_velocity_burst_after_the_threshold():
    txns = [make_txn(f"T{i}", minutes=i) for i in range(6)]
    flags = run_batch(txns, [VelocityRule(max_txns=4)])
    assert flags == [Flag("T4", "velocity"), Flag("T5", "velocity")]


def test_accounts_are_evaluated_independently():
    a = [make_txn(f"A{i}", account_id="A", minutes=i) for i in range(3)]
    b = [make_txn(f"B{i}", account_id="B", minutes=i) for i in range(3)]
    assert run_batch(a + b, [VelocityRule(max_txns=4)]) == []


def test_result_does_not_depend_on_input_order():
    txns = [make_txn(f"T{i}", minutes=i) for i in range(8)]
    shuffled = txns[:]
    random.Random(0).shuffle(shuffled)
    rules = default_rules()
    assert run_batch(txns, rules) == run_batch(shuffled, rules)


def test_no_transactions_means_no_flags():
    assert run_batch([], default_rules()) == []
