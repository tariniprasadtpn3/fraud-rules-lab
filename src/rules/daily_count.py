"""Daily-count rule: too many transactions on one calendar day."""

from __future__ import annotations

from typing import Sequence

from src.generator import Transaction

from .base import Rule


class DailyCountRule(Rule):
    """Flag a transaction when it is at least the `max_per_day`-th one that the
    account makes on the same calendar day.

    Unlike `velocity` (a sliding time window), this buckets by calendar date,
    so it catches steady high-volume days that never form a tight burst.
    """

    name = "daily_count"

    def __init__(self, max_per_day: int = 8):
        if max_per_day < 2:
            raise ValueError("max_per_day must be at least 2")
        self.max_per_day = max_per_day

    def evaluate(self, txn: Transaction, history: Sequence[Transaction]) -> bool:
        day = txn.timestamp.date()
        earlier = sum(1 for h in history if h.timestamp.date() == day)
        return earlier + 1 >= self.max_per_day
