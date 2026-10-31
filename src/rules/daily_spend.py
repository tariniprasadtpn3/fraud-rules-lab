"""Daily-spend rule: too much money spent by one account on one calendar day."""

from __future__ import annotations

from typing import Sequence

from src.generator import Transaction

from .base import Rule


class DailySpendRule(Rule):
    """Flag a transaction when the account's total spend on that calendar day,
    including this transaction, reaches `max_total`.

    Complements `daily_count` (how many) and `cumulative_spend` (a sliding
    window) by bucketing the money spent by calendar date.
    """

    name = "daily_spend"

    def __init__(self, max_total: float = 2000.0):
        if max_total <= 0:
            raise ValueError("max_total must be positive")
        self.max_total = max_total

    def evaluate(self, txn: Transaction, history: Sequence[Transaction]) -> bool:
        day = txn.timestamp.date()
        total = txn.amount + sum(h.amount for h in history if h.timestamp.date() == day)
        return total >= self.max_total
