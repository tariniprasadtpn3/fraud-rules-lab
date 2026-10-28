"""New-hour-high-amount rule: a large purchase at an hour the account never used."""

from __future__ import annotations

from typing import Sequence

from src.generator import Transaction

from .base import Rule


class NewHourHighAmountRule(Rule):
    """Flag a transaction that is at least `threshold` and happens at an hour
    of day that never appears in the account's earlier transactions.

    A stricter combination of `new_hour` and `high_amount`. Accounts with fewer
    than `min_history` earlier transactions are skipped.
    """

    name = "new_hour_high_amount"

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
        return all(h.timestamp.hour != txn.timestamp.hour for h in history)
