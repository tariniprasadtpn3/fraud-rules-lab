"""Foreign-daily-spend rule: heavy spending on one calendar day ending abroad."""

from __future__ import annotations

from collections import Counter
from typing import Sequence

from src.generator import Transaction

from .base import Rule


class ForeignDailySpendRule(Rule):
    """Flag a transaction made outside the account's most common country when
    the account's total spend on that calendar day, including this
    transaction, reaches `max_total`.

    Every transaction of the day counts, whatever its country. Accounts with
    fewer than `min_history` earlier transactions are never flagged.
    """

    name = "foreign_daily_spend"

    def __init__(self, max_total: float = 2000.0, min_history: int = 5):
        if max_total <= 0:
            raise ValueError("max_total must be positive")
        if min_history < 1:
            raise ValueError("min_history must be at least 1")
        self.max_total = max_total
        self.min_history = min_history

    def evaluate(self, txn: Transaction, history: Sequence[Transaction]) -> bool:
        if len(history) < self.min_history:
            return False
        day = txn.timestamp.date()
        total = txn.amount + sum(h.amount for h in history if h.timestamp.date() == day)
        if total < self.max_total:
            return False
        home = Counter(h.country for h in history).most_common(1)[0][0]
        return txn.country != home
