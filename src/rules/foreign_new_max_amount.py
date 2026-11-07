"""Foreign-new-max-amount rule: purchase abroad larger than any earlier one."""

from __future__ import annotations

from collections import Counter
from typing import Sequence

from src.generator import Transaction

from .base import Rule


class ForeignNewMaxAmountRule(Rule):
    """Flag a transaction made outside the account's most common country whose
    amount is larger than every amount in the account's earlier transactions.

    A record-high purchase in an unusual country is a common sign of a card
    used by someone else. Accounts with fewer than `min_history` earlier
    transactions are never flagged.
    """

    name = "foreign_new_max_amount"

    def __init__(self, min_history: int = 5):
        if min_history < 1:
            raise ValueError("min_history must be at least 1")
        self.min_history = min_history

    def evaluate(self, txn: Transaction, history: Sequence[Transaction]) -> bool:
        if len(history) < self.min_history:
            return False
        if txn.amount <= max(h.amount for h in history):
            return False
        home = Counter(h.country for h in history).most_common(1)[0][0]
        return txn.country != home
