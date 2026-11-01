"""Foreign-night rule: a purchase abroad during unusual overnight hours."""

from __future__ import annotations

from collections import Counter
from typing import Sequence

from src.generator import Transaction

from .base import Rule


class ForeignNightRule(Rule):
    """Flag a transaction made outside the account's most common country
    during the hour window [`start_hour`, `end_hour`).

    Travel and night-time activity are each normal on their own; together they
    are a classic sign of a stolen card used far from home. The window may wrap
    past midnight. Accounts with fewer than `min_history` earlier transactions
    are never flagged.
    """

    name = "foreign_night"

    def __init__(self, start_hour: int = 1, end_hour: int = 5, min_history: int = 5):
        if not (0 <= start_hour <= 23 and 0 <= end_hour <= 23):
            raise ValueError("hours must be between 0 and 23")
        if start_hour == end_hour:
            raise ValueError("start_hour and end_hour must differ")
        if min_history < 1:
            raise ValueError("min_history must be at least 1")
        self.start_hour = start_hour
        self.end_hour = end_hour
        self.min_history = min_history

    def _is_night(self, hour: int) -> bool:
        if self.start_hour < self.end_hour:
            return self.start_hour <= hour < self.end_hour
        return hour >= self.start_hour or hour < self.end_hour

    def evaluate(self, txn: Transaction, history: Sequence[Transaction]) -> bool:
        if len(history) < self.min_history or not self._is_night(txn.timestamp.hour):
            return False
        home = Counter(h.country for h in history).most_common(1)[0][0]
        return txn.country != home
