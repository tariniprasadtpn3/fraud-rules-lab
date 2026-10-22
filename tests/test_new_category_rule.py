from datetime import datetime, timedelta

import pytest

from src.generator import Transaction
from src.rules import NewCategoryRule, Rule


def _txn(i: int, category: str) -> Transaction:
    return Transaction(f"T{i}", "ACC0001", datetime(2026, 3, 1) + timedelta(hours=i), 25.0, category, "IN")


def _history(n: int, category: str = "grocery"):
    return [_txn(i, category) for i in range(n)]


def test_implements_interface():
    assert isinstance(NewCategoryRule(), Rule)
    assert NewCategoryRule().name == "new_category"


def test_flags_unseen_category():
    assert NewCategoryRule().evaluate(_txn(99, "electronics"), _history(10)) is True


def test_known_category_not_flagged():
    hist = _history(9) + [_txn(9, "fuel")]
    assert NewCategoryRule().evaluate(_txn(99, "fuel"), hist) is False


def test_short_history_never_flagged():
    assert NewCategoryRule().evaluate(_txn(99, "electronics"), _history(9)) is False


def test_custom_min_history_boundary():
    rule = NewCategoryRule(min_history=3)
    assert rule.evaluate(_txn(99, "travel"), _history(3)) is True
    assert rule.evaluate(_txn(99, "travel"), _history(2)) is False


def test_rejects_bad_min_history():
    with pytest.raises(ValueError):
        NewCategoryRule(min_history=0)
