"""Statelessness: a rule reused across many transactions must give the same
answers as a fresh instance per call (no hidden state carried between calls)."""

import inspect

import pytest

import src.rules as rules_pkg
from src.generator import generate_transactions

RULE_CLASSES = [
    getattr(rules_pkg, n)
    for n in rules_pkg.__all__
    if n != "Rule" and inspect.isclass(getattr(rules_pkg, n))
]


def _cases(seed: int = 11, limit: int = 60):
    seen: dict[str, list] = {}
    cases = []
    for txn in generate_transactions(seed=seed):
        history = seen.setdefault(txn.account_id, [])
        cases.append((txn, list(history)))
        history.append(txn)
    return cases[-limit:]


@pytest.mark.parametrize("rule_cls", RULE_CLASSES, ids=lambda c: c.name)
def test_reused_rule_matches_fresh_instance(rule_cls):
    reused = rule_cls()
    for txn, history in _cases():
        assert reused.evaluate(txn, history) == rule_cls().evaluate(txn, history)
