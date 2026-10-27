"""New-account high-amount rule: a large purchase on a barely-used account."""

from __future__ import annotations

from typing import Sequence

from src.generator import Transaction

from .base import Rule


class NewAccountHighAmountRule(Rule):
    """Flag a transaction whose amount is at least `threshold` when the account
    has fewer than `max_history` earlier transactions.

    History-based rules skip young accounts; this rule covers exactly them.
    """

    name = "new_account_high_amount"

    def __init__(self, threshold: float = 1000.0, max_history: int = 3):
        if threshold <= 0:
            raise ValueError("threshold must be positive")
        if max_history < 1:
            raise ValueError("max_history must be at least 1")
        self.threshold = threshold
        self.max_history = max_history

    def evaluate(self, txn: Transaction, history: Sequence[Transaction]) -> bool:
        return len(history) < self.max_history and txn.amount >= self.threshold
