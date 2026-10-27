"""New-country-high-amount rule: a large purchase in a never-before-used country."""

from __future__ import annotations

from typing import Sequence

from src.generator import Transaction

from .base import Rule


class NewCountryHighAmountRule(Rule):
    """Flag a transaction that is at least `threshold` and happens in a country
    the account has never used before.

    A stricter combination of `new_country` and `high_amount`: travelling with
    small purchases is ignored, only big first-time-country spends fire.
    Accounts with fewer than `min_history` earlier transactions are skipped.
    """

    name = "new_country_high_amount"

    def __init__(self, threshold: float = 300.0, min_history: int = 5):
        if threshold <= 0:
            raise ValueError("threshold must be positive")
        if min_history < 1:
            raise ValueError("min_history must be at least 1")
        self.threshold = threshold
        self.min_history = min_history

    def evaluate(self, txn: Transaction, history: Sequence[Transaction]) -> bool:
        if txn.amount < self.threshold or len(history) < self.min_history:
            return False
        return all(h.country != txn.country for h in history)
