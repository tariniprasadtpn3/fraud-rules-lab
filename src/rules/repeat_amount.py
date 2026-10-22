"""Repeat-amount rule: the same amount charged again within a short window."""

from __future__ import annotations

from datetime import timedelta
from typing import Sequence

from src.generator import Transaction

from .base import Rule


class RepeatAmountRule(Rule):
    """Flag a transaction whose amount exactly matches an earlier transaction
    of the same account made within `window` (card-testing / duplicate charge
    pattern).

    It is not part of the default batch rule set and needs no minimum history.
    """

    name = "repeat_amount"

    def __init__(self, window: timedelta = timedelta(minutes=10)):
        if window <= timedelta(0):
            raise ValueError("window must be positive")
        self.window = window

    def evaluate(self, txn: Transaction, history: Sequence[Transaction]) -> bool:
        return any(
            h.amount == txn.amount and timedelta(0) <= txn.timestamp - h.timestamp <= self.window
            for h in history
        )
