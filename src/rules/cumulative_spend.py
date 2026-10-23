"""Cumulative-spend rule: total spend inside a window exceeds a limit."""

from __future__ import annotations

from datetime import timedelta
from typing import Sequence

from src.generator import Transaction

from .base import Rule


class CumulativeSpendRule(Rule):
    """Flag a transaction when its amount plus the account's earlier spend
    within `window` is strictly above `limit` (a daily-spend-limit check).

    Catches many medium purchases that no single-amount rule would flag.
    It needs no minimum history.
    """

    name = "cumulative_spend"

    def __init__(self, limit: float = 10000.0, window: timedelta = timedelta(hours=24)):
        if limit <= 0:
            raise ValueError("limit must be positive")
        if window <= timedelta(0):
            raise ValueError("window must be positive")
        self.limit = limit
        self.window = window

    def evaluate(self, txn: Transaction, history: Sequence[Transaction]) -> bool:
        total = txn.amount + sum(
            h.amount
            for h in history
            if timedelta(0) <= txn.timestamp - h.timestamp <= self.window
        )
        return total > self.limit
