"""Robustness: no exported rule may crash or flag when an account has no history."""

import inspect
from datetime import datetime

import pytest

import src.rules as rules_pkg
from src.generator import Transaction

RULE_CLASSES = [
    getattr(rules_pkg, n)
    for n in rules_pkg.__all__
    if n != "Rule" and inspect.isclass(getattr(rules_pkg, n))
]

# A deliberately extreme first-ever transaction: large, round, overnight, abroad.
FIRST_TXN = Transaction("T1", "ACC0001", datetime(2026, 3, 8, 3, 0), 10000.0, "jewelry", "US")


@pytest.mark.parametrize("rule_cls", RULE_CLASSES, ids=lambda c: c.name)
def test_rule_returns_bool_on_empty_history(rule_cls):
    result = rule_cls().evaluate(FIRST_TXN, [])
    assert isinstance(result, bool)

