"""New-weekday-high-amount rule: a large purchase on a weekday the account never used."""

from __future__ import annotations

from typing import Sequence

from src.generator import Transaction

from .base import Rule


class NewWeekdayHighAmountRule(Rule):
    """Flag a transaction that is at least `threshold` and happens on a day of
    the week that never appears in the account's earlier transactions.

    Accounts with fewer than `min_history` earlier transactions are skipped.
    """

    name = "new_weekday_high_amount"

    def __init__(self, threshold: float = 300.0, min_history: int = 14):
        if threshold <= 0:
            raise ValueError("threshold must be positive")
        if min_history < 1:
            raise ValueError("min_history must be at least 1")
        self.threshold = threshold
        self.min_history = min_history

    def evaluate(self, txn: Transaction, history: Sequence[Transaction]) -> bool:
        if txn.amount < self.threshold or len(history) < self.min_history:
            return False
        day = txn.timestamp.weekday()
        return all(h.timestamp.weekday() != day for h in history)
