from datetime import datetime

import pytest

from src.generator import Transaction
from src.rules import ForeignNewCategoryRule, Rule


def _txn(category: str, country: str) -> Transaction:
    return Transaction("T1", "ACC0001", datetime(2026, 3, 9, 14, 0), 50.0, category, country)


HISTORY = [_txn("grocery", "IN") for _ in range(6)]


def test_implements_interface():
    assert isinstance(ForeignNewCategoryRule(), Rule)
    assert ForeignNewCategoryRule().name == "foreign_new_category"


def test_flags_foreign_new_category():
    assert ForeignNewCategoryRule().evaluate(_txn("jewelry", "US"), HISTORY) is True


def test_ignores_known_category_abroad():
    assert ForeignNewCategoryRule().evaluate(_txn("grocery", "US"), HISTORY) is False


def test_ignores_new_category_at_home():
    assert ForeignNewCategoryRule().evaluate(_txn("jewelry", "IN"), HISTORY) is False


def test_needs_min_history():
    assert ForeignNewCategoryRule().evaluate(_txn("jewelry", "US"), HISTORY[:4]) is False
    assert ForeignNewCategoryRule(min_history=2).evaluate(_txn("jewelry", "US"), HISTORY[:2]) is True


def test_invalid_parameter():
    with pytest.raises(ValueError):
        ForeignNewCategoryRule(min_history=0)
