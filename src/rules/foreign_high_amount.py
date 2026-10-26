"""Foreign-high-amount rule: a large purchase outside the account's home country."""

from __future__ import annotations

from collections import Counter
from typing import Sequence

from src.generator import Transaction

from .base import Rule


class ForeignHighAmountRule(Rule):
    """Flag a transaction whose country differs from the account's most common
    country and whose amount is at least `threshold`.

    Small purchases abroad are normal (travel), so only large ones are flagged.
    Accounts with fewer than `min_history` earlier transactions are never flagged.
    """

    name = "foreign_high_amount"

    def __init__(self, threshold: float = 300.0, min_history: int = 5):
        if threshold <= 0:
            raise ValueError("threshold must be positive")
        if min_history < 1:
            raise ValueError("min_history must be at least 1")
        self.threshold = threshold
        self.min_history = min_history

    def evaluate(self, txn: Transaction, history: Sequence[Transaction]) -> bool:
        if len(history) < self.min_history or txn.amount < self.threshold:
            return False
        home = Counter(h.country for h in history).most_common(1)[0][0]
        return txn.country != home
