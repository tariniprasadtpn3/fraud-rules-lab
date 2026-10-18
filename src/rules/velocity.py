"""Velocity rule: too many transactions on one account in a short window."""

from __future__ import annotations

from datetime import timedelta
from typing import Sequence

from src.generator import Transaction

from .base import Rule


class VelocityRule(Rule):
    """Flag a transaction when it is the `min_count`-th or later one inside `window`.

    The count includes the transaction being evaluated, so with the defaults
    the third purchase within five minutes is the first one flagged.
    """

    name = "velocity"

    def __init__(self, min_count: int = 3, window: timedelta = timedelta(minutes=5)):
        if min_count < 2:
            raise ValueError("min_count must be at least 2")
        if window <= timedelta(0):
            raise ValueError("window must be positive")
        self.min_count = min_count
        self.window = window

    def evaluate(self, txn: Transaction, history: Sequence[Transaction]) -> bool:
        cutoff = txn.timestamp - self.window
        recent = sum(1 for h in history if cutoff <= h.timestamp <= txn.timestamp)
        return recent + 1 >= self.min_count
