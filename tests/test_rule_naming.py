"""Housekeeping: rule names follow one convention."""

import inspect
import re

import src.rules as rules_pkg

RULE_CLASSES = [
    getattr(rules_pkg, n)
    for n in rules_pkg.__all__
    if n != "Rule" and inspect.isclass(getattr(rules_pkg, n))
]


def test_rule_names_are_snake_case():
    for cls in RULE_CLASSES:
        assert re.fullmatch(r"[a-z][a-z0-9_]*", cls.name), cls.name

