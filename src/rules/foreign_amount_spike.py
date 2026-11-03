"""Foreign-amount-spike rule: purchase abroad far above the account's average."""

from __future__ import annotations

from collections import Counter
from typing import Sequence

from src.generator import Transaction

from .base import Rule


class ForeignAmountSpikeRule(Rule):
    """Flag a transaction made outside the account's most common country whose
    amount exceeds `multiplier` times the account's average earlier amount.

    Accounts with fewer than `min_history` earlier transactions are never
    flagged.
    """

    name = "foreign_amount_spike"

    def __init__(self, multiplier: float = 3.0, min_history: int = 5):
        if multiplier <= 1.0:
            raise ValueError("multiplier must be greater than 1")
        if min_history < 1:
            raise ValueError("min_history must be at least 1")
        self.multiplier = multiplier
        self.min_history = min_history

    def evaluate(self, txn: Transaction, history: Sequence[Transaction]) -> bool:
        if len(history) < self.min_history:
            return False
        home = Counter(h.country for h in history).most_common(1)[0][0]
        if txn.country == home:
            return False
        average = sum(h.amount for h in history) / len(history)
        return txn.amount > self.multiplier * average
