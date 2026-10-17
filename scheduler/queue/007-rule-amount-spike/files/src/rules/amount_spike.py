from __future__ import annotations

from datetime import timedelta
from typing import Sequence

from src.generator.models import Transaction

from .base import Rule, within


class AmountSpikeRule(Rule):
    """Flag an amount greater than ``multiplier`` times the recent average.

    Needs at least ``min_history`` earlier transactions inside ``window`` so
    that brand-new accounts are not flagged on thin evidence.
    """

    name = "amount_spike"

    def __init__(
        self,
        multiplier: float = 5.0,
        min_history: int = 5,
        window: timedelta = timedelta(days=30),
    ):
        self.multiplier = multiplier
        self.min_history = min_history
        self.window = window
        self.lookback = window

    def evaluate(self, txn: Transaction, history: Sequence[Transaction]) -> bool:
        recent = within(history, txn.timestamp, self.window)
        if len(recent) < self.min_history:
            return False
        mean = sum(t.amount for t in recent) / len(recent)
        return txn.amount > self.multiplier * mean
