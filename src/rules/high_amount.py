"""High amount rule: a single purchase above a fixed ceiling."""

from __future__ import annotations

from typing import Sequence

from src.generator import Transaction

from .base import Rule


class HighAmountRule(Rule):
    """Flag a transaction whose amount is strictly above `threshold`.

    Unlike the amount spike rule this needs no history, so it also covers
    brand-new accounts.
    """

    name = "high_amount"

    def __init__(self, threshold: float = 5000.0):
        if threshold <= 0:
            raise ValueError("threshold must be positive")
        self.threshold = threshold

    def evaluate(self, txn: Transaction, history: Sequence[Transaction]) -> bool:
        return txn.amount > self.threshold
