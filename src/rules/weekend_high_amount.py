"""Weekend-high-amount rule: a large purchase on a Saturday or Sunday."""

from __future__ import annotations

from typing import Sequence

from src.generator import Transaction

from .base import Rule


class WeekendHighAmountRule(Rule):
    """Flag a transaction made on a weekend whose amount is at least `threshold`.

    Weekends are less monitored by humans, so a lower bar than a plain
    fixed-threshold rule can be used there. It needs no history.
    """

    name = "weekend_high_amount"

    def __init__(self, threshold: float = 500.0):
        if threshold <= 0:
            raise ValueError("threshold must be positive")
        self.threshold = threshold

    def evaluate(self, txn: Transaction, history: Sequence[Transaction]) -> bool:
        return txn.timestamp.weekday() >= 5 and txn.amount >= self.threshold
