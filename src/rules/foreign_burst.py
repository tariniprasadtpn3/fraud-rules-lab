"""Foreign-burst rule: several purchases abroad in a short window."""

from __future__ import annotations

from collections import Counter
from datetime import timedelta
from typing import Sequence

from src.generator import Transaction

from .base import Rule


class ForeignBurstRule(Rule):
    """Flag a transaction made outside the account's most common country when
    the account already made at least `min_count - 1` other transactions
    outside that country within the previous `window_minutes` minutes.

    Accounts with fewer than `min_history` earlier transactions are never
    flagged.
    """

    name = "foreign_burst"

    def __init__(self, min_count: int = 3, window_minutes: int = 60, min_history: int = 5):
        if min_count < 2:
            raise ValueError("min_count must be at least 2")
        if window_minutes < 1:
            raise ValueError("window_minutes must be at least 1")
        if min_history < 1:
            raise ValueError("min_history must be at least 1")
        self.min_count = min_count
        self.window = timedelta(minutes=window_minutes)
        self.min_history = min_history

    def evaluate(self, txn: Transaction, history: Sequence[Transaction]) -> bool:
        if len(history) < self.min_history:
            return False
        home = Counter(h.country for h in history).most_common(1)[0][0]
        if txn.country == home:
            return False
        recent = sum(
            1
            for h in history
            if h.country != home and timedelta(0) <= txn.timestamp - h.timestamp <= self.window
        )
        return recent + 1 >= self.min_count
