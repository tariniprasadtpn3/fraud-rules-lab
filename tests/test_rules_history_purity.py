"""Purity: rules must not mutate the history they are given, and must give the
same answer whether history arrives as a list or a tuple."""

import inspect

import pytest

import src.rules as rules_pkg
from src.generator import generate_transactions

RULE_CLASSES = [
    getattr(rules_pkg, n)
    for n in rules_pkg.__all__
    if n != "Rule" and inspect.isclass(getattr(rules_pkg, n))
]


def _per_account_cases(seed: int = 7, limit: int = 40):
    """Yield (txn, earlier-transactions-of-same-account) pairs from synthetic data."""
    seen: dict[str, list] = {}
    cases = []
    for txn in generate_transactions(seed=seed):
        history = seen.setdefault(txn.account_id, [])
        if history:
            cases.append((txn, list(history)))
        history.append(txn)
    return cases[-limit:]


@pytest.mark.parametrize("rule_cls", RULE_CLASSES, ids=lambda c: c.name)
def test_rule_does_not_mutate_history_and_ignores_container_type(rule_cls):
    rule = rule_cls()
    for txn, history in _per_account_cases():
        snapshot = list(history)
        as_list = rule.evaluate(txn, history)
        assert history == snapshot
        assert rule.evaluate(txn, tuple(history)) == as_list
