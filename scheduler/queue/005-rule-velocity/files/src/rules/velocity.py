from __future__ import annotations

from datetime import timedelta
from typing import Sequence

from src.generator.models import Transaction

from .base import Rule, within


class VelocityRule(Rule):
    """Flag a transaction that pushes an account over ``max_txns`` in ``window``.

    The current transaction counts towards the total, so with the defaults the
    5th transaction inside ten minutes is the first one flagged.
    """

    name = "velocity"

    def __init__(self, max_txns: int = 4, window: timedelta = timedelta(minutes=10)):
        self.max_txns = max_txns
        self.window = window
        self.lookback = window

    def evaluate(self, txn: Transaction, history: Sequence[Transaction]) -> bool:
        recent = within(history, txn.timestamp, self.window)
        return len(recent) + 1 > self.max_txns
