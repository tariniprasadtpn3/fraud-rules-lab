"""Median-spike rule: amount far above the median of the account's earlier amounts."""

from __future__ import annotations

from statistics import median
from typing import Sequence

from src.generator import Transaction

from .base import Rule


class MedianSpikeRule(Rule):
    """Flag a transaction whose amount is more than `multiplier` times the
    median of the account's earlier amounts.

    The median is robust to a few earlier outliers, unlike the mean used by
    `amount_spike`. Accounts with fewer than `min_history` earlier
    transactions are skipped.
    """

    name = "median_spike"

    def __init__(self, multiplier: float = 5.0, min_history: int = 5):
        if multiplier <= 1:
            raise ValueError("multiplier must be greater than 1")
        if min_history < 1:
            raise ValueError("min_history must be at least 1")
        self.multiplier = multiplier
        self.min_history = min_history

    def evaluate(self, txn: Transaction, history: Sequence[Transaction]) -> bool:
        if len(history) < self.min_history:
            return False
        return txn.amount > self.multiplier * median(h.amount for h in history)
