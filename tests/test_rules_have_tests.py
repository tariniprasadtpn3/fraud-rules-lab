"""Housekeeping: every exported rule has its own test module and a README mention."""

import inspect
from pathlib import Path

import pytest

import src.rules as rules_pkg

ROOT = Path(__file__).resolve().parent.parent
RULE_CLASSES = [
    getattr(rules_pkg, n)
    for n in rules_pkg.__all__
    if n != "Rule" and inspect.isclass(getattr(rules_pkg, n))
]


@pytest.mark.parametrize("rule_cls", RULE_CLASSES, ids=lambda c: c.name)
def test_rule_has_dedicated_test_module(rule_cls):
    assert (ROOT / "tests" / f"test_{rule_cls.name}_rule.py").exists()


def test_every_extra_rule_is_listed_in_readme():
    core = {"velocity", "amount_spike", "geo_mismatch", "dormant_reactivation"}
    readme = (ROOT / "README.md").read_text()
    missing = [c.name for c in RULE_CLASSES if c.name not in core and c.name not in readme]
    assert not missing, f"rules missing from README: {missing}"
