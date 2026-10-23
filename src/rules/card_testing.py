"""Card-testing rule: a burst of tiny transactions in a short window."""

from __future__ import annotations

from datetime import timedelta
from typing import Sequence

from src.generator import Transaction

from .base import Rule


class CardTestingRule(Rule):
    """Flag a small transaction that follows several other small ones quickly.

    Fraudsters often probe a stolen card with a few tiny purchases. The rule
    flags a transaction of at most `max_amount` when at least `min_count - 1`
    earlier small transactions fall inside `window` (the current one counts).
    """

    name = "card_testing"

    def __init__(
        self,
        max_amount: float = 5.0,
        min_count: int = 3,
        window: timedelta = timedelta(minutes=10),
    ):
        if max_amount <= 0:
            raise ValueError("max_amount must be positive")
        if min_count < 2:
            raise ValueError("min_count must be at least 2")
        if window <= timedelta(0):
            raise ValueError("window must be positive")
        self.max_amount = max_amount
        self.min_count = min_count
        self.window = window

    def evaluate(self, txn: Transaction, history: Sequence[Transaction]) -> bool:
        if txn.amount > self.max_amount:
            return False
        cutoff = txn.timestamp - self.window
        small = sum(
            1 for h in history if h.amount <= self.max_amount and cutoff <= h.timestamp <= txn.timestamp
        )
        return small + 1 >= self.min_count
