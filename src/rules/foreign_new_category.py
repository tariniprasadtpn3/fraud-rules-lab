"""Foreign-new-category rule: purchase abroad in a category the account never used."""

from __future__ import annotations

from collections import Counter
from typing import Sequence

from src.generator import Transaction

from .base import Rule


class ForeignNewCategoryRule(Rule):
    """Flag a transaction made outside the account's most common country in a
    merchant category that does not appear in the account's earlier transactions.

    Either signal alone is common (travel, trying a new shop); together they
    point to a card used by someone with different habits. Accounts with fewer
    than `min_history` earlier transactions are never flagged.
    """

    name = "foreign_new_category"

    def __init__(self, min_history: int = 5):
        if min_history < 1:
            raise ValueError("min_history must be at least 1")
        self.min_history = min_history

    def evaluate(self, txn: Transaction, history: Sequence[Transaction]) -> bool:
        if len(history) < self.min_history:
            return False
        home = Counter(h.country for h in history).most_common(1)[0][0]
        if txn.country == home:
            return False
        return txn.merchant_category not in {h.merchant_category for h in history}
