"""High-amount burst rule: several large purchases in a short window."""

from __future__ import annotations

from datetime import timedelta
from typing import Sequence

from src.generator import Transaction

from .base import Rule


class HighAmountBurstRule(Rule):
    """Flag a transaction whose amount is at least `threshold` when the account
    already made at least `min_count - 1` other transactions of at least
    `threshold` within the previous `window_minutes` minutes.

    One large purchase is normal; several in quick succession look like an
    account being drained. Only large transactions count towards the burst.
    """

    name = "high_amount_burst"

    def __init__(self, threshold: float = 300.0, min_count: int = 3, window_minutes: int = 60):
        if threshold <= 0:
            raise ValueError("threshold must be positive")
        if min_count < 2:
            raise ValueError("min_count must be at least 2")
        if window_minutes < 1:
            raise ValueError("window_minutes must be at least 1")
        self.threshold = threshold
        self.min_count = min_count
        self.window = timedelta(minutes=window_minutes)

    def evaluate(self, txn: Transaction, history: Sequence[Transaction]) -> bool:
        if txn.amount < self.threshold:
            return False
        recent = sum(
            1
            for h in history
            if h.amount >= self.threshold and timedelta(0) <= txn.timestamp - h.timestamp <= self.window
        )
        return recent + 1 >= self.min_count
