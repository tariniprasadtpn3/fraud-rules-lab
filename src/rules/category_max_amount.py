"""Category-max-amount rule: a purchase far above the account's largest one in that category."""

from __future__ import annotations

from typing import Sequence

from src.generator import Transaction

from .base import Rule


class CategoryMaxAmountRule(Rule):
    """Flag a transaction whose amount exceeds `factor` times the largest
    earlier amount the account spent in the same category.

    Like `new_max_amount`, but scoped per category, so a normally large
    category (travel) does not hide a spike in a normally small one (grocery).
    Needs at least `min_history` earlier transactions in that category.
    """

    name = "category_max_amount"

    def __init__(self, factor: float = 2.0, min_history: int = 3):
        if factor <= 1:
            raise ValueError("factor must be greater than 1")
        if min_history < 1:
            raise ValueError("min_history must be at least 1")
        self.factor = factor
        self.min_history = min_history

    def evaluate(self, txn: Transaction, history: Sequence[Transaction]) -> bool:
        same = [h.amount for h in history if h.merchant_category == txn.merchant_category]
        if len(same) < self.min_history:
            return False
        return txn.amount > self.factor * max(same)
