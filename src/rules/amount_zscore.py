"""Amount z-score rule: a purchase statistically far from the account's usual amounts."""

from __future__ import annotations

import statistics
from typing import Sequence

from src.generator import Transaction

from .base import Rule


class AmountZScoreRule(Rule):
    """Flag a transaction whose amount is more than `threshold` standard
    deviations above the mean of the account's earlier amounts.

    Unlike `amount_spike` (a fixed multiple of the average), this adapts to how
    variable the account is: the same amount can be normal for a volatile
    account and an outlier for a steady one. Accounts with fewer than
    `min_history` earlier transactions, or with zero spread, are never flagged.
    """

    name = "amount_zscore"

    def __init__(self, threshold: float = 3.0, min_history: int = 10):
        if threshold <= 0:
            raise ValueError("threshold must be positive")
        if min_history < 2:
            raise ValueError("min_history must be at least 2")
        self.threshold = threshold
        self.min_history = min_history

    def evaluate(self, txn: Transaction, history: Sequence[Transaction]) -> bool:
        if len(history) < self.min_history:
            return False
        amounts = [h.amount for h in history]
        stdev = statistics.pstdev(amounts)
        if stdev == 0:
            return False
        return (txn.amount - statistics.fmean(amounts)) / stdev > self.threshold
