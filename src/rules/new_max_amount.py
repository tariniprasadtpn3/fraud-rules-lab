"""New-max-amount rule: a purchase far above the account's largest earlier one."""

from __future__ import annotations

from typing import Sequence

from src.generator import Transaction

from .base import Rule


class NewMaxAmountRule(Rule):
    """Flag a transaction whose amount exceeds `factor` times the largest
    amount in the account's earlier transactions.

    Unlike `amount_spike` (compares with the average), this compares with the
    historical maximum, so accounts with naturally wide spending are not
    flagged for ordinary large purchases. Accounts with fewer than
    `min_history` earlier transactions are never flagged.
    """

    name = "new_max_amount"

    def __init__(self, factor: float = 1.5, min_history: int = 5):
        if factor <= 1:
            raise ValueError("factor must be greater than 1")
        if min_history < 1:
            raise ValueError("min_history must be at least 1")
        self.factor = factor
        self.min_history = min_history

    def evaluate(self, txn: Transaction, history: Sequence[Transaction]) -> bool:
        if len(history) < self.min_history:
            return False
        return txn.amount > self.factor * max(h.amount for h in history)
