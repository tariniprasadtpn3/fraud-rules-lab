"""New-category-high-amount rule: a large purchase in a never-used merchant category."""

from __future__ import annotations

from typing import Sequence

from src.generator import Transaction

from .base import Rule


class NewCategoryHighAmountRule(Rule):
    """Flag a transaction that is at least `threshold` and falls in a merchant
    category the account has never used before.

    A stricter combination of `new_category` and `high_amount`: trying a new
    kind of merchant with a small purchase is ignored, only big first-time
    category spends fire. Accounts with fewer than `min_history` earlier
    transactions are skipped.
    """

    name = "new_category_high_amount"

    def __init__(self, threshold: float = 300.0, min_history: int = 10):
        if threshold <= 0:
            raise ValueError("threshold must be positive")
        if min_history < 1:
            raise ValueError("min_history must be at least 1")
        self.threshold = threshold
        self.min_history = min_history

    def evaluate(self, txn: Transaction, history: Sequence[Transaction]) -> bool:
        if txn.amount < self.threshold or len(history) < self.min_history:
            return False
        return all(h.merchant_category != txn.merchant_category for h in history)
