"""Amount spike rule: a purchase far above the account's usual amount."""

from __future__ import annotations

from typing import Sequence

from src.generator import Transaction

from .base import Rule


class AmountSpikeRule(Rule):
    """Flag a transaction whose amount exceeds `multiplier` times the account's
    average earlier amount.

    Accounts with fewer than `min_history` earlier transactions are never
    flagged, because there is not enough data to define "usual".
    """

    name = "amount_spike"

    def __init__(self, multiplier: float = 4.0, min_history: int = 5):
        if multiplier <= 1.0:
            raise ValueError("multiplier must be greater than 1")
        if min_history < 1:
            raise ValueError("min_history must be at least 1")
        self.multiplier = multiplier
        self.min_history = min_history

    def evaluate(self, txn: Transaction, history: Sequence[Transaction]) -> bool:
        if len(history) < self.min_history:
            return False
        average = sum(h.amount for h in history) / len(history)
        return txn.amount > self.multiplier * average
