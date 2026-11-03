"""Foreign-new-weekday rule: purchase abroad on a day of week never used."""

from __future__ import annotations

from collections import Counter
from typing import Sequence

from src.generator import Transaction

from .base import Rule


class ForeignNewWeekdayRule(Rule):
    """Flag a transaction made outside the account's most common country on a
    day of the week that never appears in the account's earlier transactions.

    Accounts with fewer than `min_history` earlier transactions are never
    flagged.
    """

    name = "foreign_new_weekday"

    def __init__(self, min_history: int = 10):
        if min_history < 1:
            raise ValueError("min_history must be at least 1")
        self.min_history = min_history

    def evaluate(self, txn: Transaction, history: Sequence[Transaction]) -> bool:
        if len(history) < self.min_history:
            return False
        home = Counter(h.country for h in history).most_common(1)[0][0]
        if txn.country == home:
            return False
        return all(h.timestamp.weekday() != txn.timestamp.weekday() for h in history)
