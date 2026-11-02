"""Foreign-weekend rule: purchase abroad on a Saturday or Sunday."""

from __future__ import annotations

from collections import Counter
from typing import Sequence

from src.generator import Transaction

from .base import Rule


class ForeignWeekendRule(Rule):
    """Flag a transaction made on a weekend outside the account's most common
    country whose amount is at least `min_amount`.

    Weekend activity abroad gets less manual review, so a modest amount is
    already worth a look. Accounts with fewer than `min_history` earlier
    transactions are never flagged.
    """

    name = "foreign_weekend"

    def __init__(self, min_amount: float = 200.0, min_history: int = 5):
        if min_amount < 0:
            raise ValueError("min_amount must not be negative")
        if min_history < 1:
            raise ValueError("min_history must be at least 1")
        self.min_amount = min_amount
        self.min_history = min_history

    def evaluate(self, txn: Transaction, history: Sequence[Transaction]) -> bool:
        if len(history) < self.min_history or txn.amount < self.min_amount:
            return False
        if txn.timestamp.weekday() < 5:
            return False
        home = Counter(h.country for h in history).most_common(1)[0][0]
        return txn.country != home
