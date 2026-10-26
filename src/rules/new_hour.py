"""New-hour rule: a purchase at an hour of day the account has never used."""

from __future__ import annotations

from typing import Sequence

from src.generator import Transaction

from .base import Rule


class NewHourRule(Rule):
    """Flag a transaction whose hour of day never appears in the account's
    earlier transactions. Accounts with fewer than `min_history` earlier
    transactions are never flagged.
    """

    name = "new_hour"

    def __init__(self, min_history: int = 10):
        if min_history < 1:
            raise ValueError("min_history must be at least 1")
        self.min_history = min_history

    def evaluate(self, txn: Transaction, history: Sequence[Transaction]) -> bool:
        if len(history) < self.min_history:
            return False
        return all(h.timestamp.hour != txn.timestamp.hour for h in history)
