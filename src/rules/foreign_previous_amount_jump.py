"""Foreign-previous-amount-jump rule: sudden step-up in amount, made abroad."""

from __future__ import annotations

from collections import Counter
from typing import Sequence

from src.generator import Transaction

from .base import Rule


class ForeignPreviousAmountJumpRule(Rule):
    """Flag a transaction made outside the account's most common country whose
    amount is at least `ratio` times the account's immediately preceding
    transaction.

    A sudden step-up in amount combined with an unusual country is a common
    sign of a card used by someone else. Accounts with fewer than
    `min_history` earlier transactions are never flagged.
    """

    name = "foreign_previous_amount_jump"

    def __init__(self, ratio: float = 5.0, min_history: int = 5):
        if ratio <= 1:
            raise ValueError("ratio must be greater than 1")
        if min_history < 1:
            raise ValueError("min_history must be at least 1")
        self.ratio = ratio
        self.min_history = min_history

    def evaluate(self, txn: Transaction, history: Sequence[Transaction]) -> bool:
        if len(history) < self.min_history:
            return False
        if txn.amount < self.ratio * history[-1].amount:
            return False
        home = Counter(h.country for h in history).most_common(1)[0][0]
        return txn.country != home
