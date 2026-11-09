"""Housekeeping: every rule module on disk is exported from src.rules."""

import importlib
import inspect
import pkgutil

import src.rules as rules_pkg

NON_RULE_MODULES = {"base"}


def _rule_modules():
    return sorted(
        m.name for m in pkgutil.iter_modules(rules_pkg.__path__) if m.name not in NON_RULE_MODULES
    )


def test_every_rule_module_exports_a_rule_class_listed_in_all():
    for mod_name in _rule_modules():
        module = importlib.import_module(f"src.rules.{mod_name}")
        classes = [
            c
            for _, c in inspect.getmembers(module, inspect.isclass)
            if c.__module__ == module.__name__ and c is not rules_pkg.Rule
        ]
        assert classes, f"{mod_name} defines no rule class"
        for cls in classes:
            assert cls.__name__ in rules_pkg.__all__, f"{cls.__name__} missing from src.rules.__all__"
            assert getattr(rules_pkg, cls.__name__) is cls
