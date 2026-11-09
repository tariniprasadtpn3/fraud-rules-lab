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



def test_rule_names_are_unique():
    names = [cls.name for cls in RULE_CLASSES]
    assert len(names) == len(set(names))


def test_rules_have_docstrings():
    for cls in RULE_CLASSES:
        assert inspect.getdoc(cls), cls.__name__


def test_every_rule_is_documented_in_rules_md():
    from pathlib import Path

    docs = (Path(__file__).resolve().parent.parent / "docs" / "rules.md").read_text()
    missing = [cls.name for cls in RULE_CLASSES if f"`{cls.name}`" not in docs]
    assert not missing, missing
