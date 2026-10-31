"""Previous-amount-jump rule: an amount many times larger than the one just before it."""

from __future__ import annotations

from typing import Sequence

from src.generator import Transaction

from .base import Rule


class PreviousAmountJumpRule(Rule):
    """Flag a transaction whose amount is at least `ratio` times the account's
    immediately preceding transaction and strictly above `min_amount`.

    Unlike `amount_spike` (compared with the account's average), this looks
    only at the last transaction, so it catches a sudden step-up even on
    accounts with a mixed history. Accounts with no earlier transactions are
    never flagged.
    """

    name = "previous_amount_jump"

    def __init__(self, ratio: float = 5.0, min_amount: float = 200.0):
        if ratio <= 1:
            raise ValueError("ratio must be greater than 1")
        if min_amount < 0:
            raise ValueError("min_amount must not be negative")
        self.ratio = ratio
        self.min_amount = min_amount

    def evaluate(self, txn: Transaction, history: Sequence[Transaction]) -> bool:
        if not history or txn.amount <= self.min_amount:
            return False
        return txn.amount >= self.ratio * history[-1].amount
