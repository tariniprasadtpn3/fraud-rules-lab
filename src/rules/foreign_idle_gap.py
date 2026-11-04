"""Foreign-idle-gap rule: purchase abroad right after a quiet spell."""

from __future__ import annotations

from collections import Counter
from datetime import timedelta
from typing import Sequence

from src.generator import Transaction

from .base import Rule


class ForeignIdleGapRule(Rule):
    """Flag a transaction made outside the account's most common country whose
    amount is at least `min_amount` and that comes at least `gap_days` after
    the account's previous transaction.

    An account that wakes up abroad after days of silence is a classic sign of
    a card used by someone else. Accounts with fewer than `min_history`
    earlier transactions are never flagged.
    """

    name = "foreign_idle_gap"

    def __init__(self, min_amount: float = 100.0, gap_days: int = 5, min_history: int = 5):
        if min_amount < 0:
            raise ValueError("min_amount must not be negative")
        if gap_days < 1:
            raise ValueError("gap_days must be at least 1")
        if min_history < 1:
            raise ValueError("min_history must be at least 1")
        self.min_amount = min_amount
        self.gap_days = gap_days
        self.min_history = min_history

    def evaluate(self, txn: Transaction, history: Sequence[Transaction]) -> bool:
        if len(history) < self.min_history or txn.amount < self.min_amount:
            return False
        if txn.timestamp - history[-1].timestamp < timedelta(days=self.gap_days):
            return False
        home = Counter(h.country for h in history).most_common(1)[0][0]
        return txn.country != home
