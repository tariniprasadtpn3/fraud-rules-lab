"""Foreign-round-amount rule: large round-number purchase abroad."""

from __future__ import annotations

from collections import Counter
from typing import Sequence

from src.generator import Transaction

from .base import Rule


class ForeignRoundAmountRule(Rule):
    """Flag a transaction made outside the account's most common country whose
    amount is at least `min_amount` and an exact multiple of `step`.

    Round large amounts and foreign locations are each weak signals; together
    they resemble scripted or manually keyed use of a stolen card. Accounts
    with fewer than `min_history` earlier transactions are never flagged.
    """

    name = "foreign_round_amount"

    def __init__(self, step: float = 500.0, min_amount: float = 1000.0, min_history: int = 5):
        if step <= 0:
            raise ValueError("step must be positive")
        if min_amount < 0:
            raise ValueError("min_amount must not be negative")
        if min_history < 1:
            raise ValueError("min_history must be at least 1")
        self.step = step
        self.min_amount = min_amount
        self.min_history = min_history

    def evaluate(self, txn: Transaction, history: Sequence[Transaction]) -> bool:
        if len(history) < self.min_history or txn.amount < self.min_amount:
            return False
        if round(txn.amount * 100) % round(self.step * 100) != 0:
            return False
        home = Counter(h.country for h in history).most_common(1)[0][0]
        return txn.country != home
