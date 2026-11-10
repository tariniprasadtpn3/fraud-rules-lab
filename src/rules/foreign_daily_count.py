"""Foreign-daily-count rule: many purchases abroad on one calendar day."""

from __future__ import annotations

from collections import Counter
from typing import Sequence

from src.generator import Transaction

from .base import Rule


class ForeignDailyCountRule(Rule):
    """Flag a transaction made outside the account's most common country when
    it is at least the `max_per_day`-th transaction the account makes on the
    same calendar day (counting itself).

    Every transaction of the day is counted, whatever its country, so a busy
    day that ends abroad is caught. Accounts with fewer than `min_history` earlier
    transactions are never flagged.
    """

    name = "foreign_daily_count"

    def __init__(self, max_per_day: int = 5, min_history: int = 5):
        if max_per_day < 2:
            raise ValueError("max_per_day must be at least 2")
        if min_history < 1:
            raise ValueError("min_history must be at least 1")
        self.max_per_day = max_per_day
        self.min_history = min_history

    def evaluate(self, txn: Transaction, history: Sequence[Transaction]) -> bool:
        if len(history) < self.min_history:
            return False
        day = txn.timestamp.date()
        if 1 + sum(1 for h in history if h.timestamp.date() == day) < self.max_per_day:
            return False
        home = Counter(h.country for h in history).most_common(1)[0][0]
        return txn.country != home
