"""Foreign-repeat-amount rule: the same amount charged again abroad in a short window."""

from __future__ import annotations

from collections import Counter
from datetime import timedelta
from typing import Sequence

from src.generator import Transaction

from .base import Rule


class ForeignRepeatAmountRule(Rule):
    """Flag a transaction made outside the account's most common country whose
    amount exactly matches an earlier transaction of the same account made
    within `window` (duplicate-charge pattern on a card used abroad).

    Accounts with fewer than `min_history` earlier transactions are never
    flagged.
    """

    name = "foreign_repeat_amount"

    def __init__(self, window: timedelta = timedelta(minutes=10), min_history: int = 5):
        if window <= timedelta(0):
            raise ValueError("window must be positive")
        if min_history < 1:
            raise ValueError("min_history must be at least 1")
        self.window = window
        self.min_history = min_history

    def evaluate(self, txn: Transaction, history: Sequence[Transaction]) -> bool:
        if len(history) < self.min_history:
            return False
        home = Counter(h.country for h in history).most_common(1)[0][0]
        if txn.country == home:
            return False
        return any(
            h.amount == txn.amount and timedelta(0) <= txn.timestamp - h.timestamp <= self.window
            for h in history
        )
