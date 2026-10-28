"""Night-high-amount rule: a large purchase during unusual overnight hours."""

from __future__ import annotations

from typing import Sequence

from src.generator import Transaction

from .base import Rule


class NightHighAmountRule(Rule):
    """Flag a transaction that is at least `threshold` and happens in the
    hour window [`start_hour`, `end_hour`).

    A stricter combination of `night_hours` and `high_amount`: small night-time
    purchases are ignored, only big ones fire. The window may wrap past
    midnight (for example 23 to 5). It needs no history.
    """

    name = "night_high_amount"

    def __init__(self, threshold: float = 300.0, start_hour: int = 1, end_hour: int = 5):
        if threshold <= 0:
            raise ValueError("threshold must be positive")
        if not (0 <= start_hour <= 23 and 0 <= end_hour <= 23):
            raise ValueError("hours must be between 0 and 23")
        if start_hour == end_hour:
            raise ValueError("start_hour and end_hour must differ")
        self.threshold = threshold
        self.start_hour = start_hour
        self.end_hour = end_hour

    def evaluate(self, txn: Transaction, history: Sequence[Transaction]) -> bool:
        if txn.amount < self.threshold:
            return False
        hour = txn.timestamp.hour
        if self.start_hour < self.end_hour:
            return self.start_hour <= hour < self.end_hour
        return hour >= self.start_hour or hour < self.end_hour
