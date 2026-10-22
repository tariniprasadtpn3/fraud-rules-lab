"""Round-amount rule: large amounts that are exact multiples of a round step."""

from __future__ import annotations

from typing import Sequence

from src.generator import Transaction

from .base import Rule


class RoundAmountRule(Rule):
    """Flag a transaction whose amount is at least `min_amount` and an exact
    multiple of `step` (for example 1000.00, 2500.00 with `step=500`).

    Genuine purchases rarely land on perfectly round large values, while
    manually keyed or scripted transfers often do. It needs no history and is

    """

    name = "round_amount"

    def __init__(self, step: float = 500.0, min_amount: float = 1000.0):
        if step <= 0:
            raise ValueError("step must be positive")
        if min_amount < 0:
            raise ValueError("min_amount must not be negative")
        self.step = step
        self.min_amount = min_amount

    def evaluate(self, txn: Transaction, history: Sequence[Transaction]) -> bool:
        if txn.amount < self.min_amount:
            return False
        cents = round(txn.amount * 100)
        step_cents = round(self.step * 100)
        return step_cents > 0 and cents % step_cents == 0
