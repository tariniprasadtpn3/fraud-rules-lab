"""New-category rule: first purchase in a merchant category the account never used."""

from __future__ import annotations

from typing import Sequence

from src.generator import Transaction

from .base import Rule


class NewCategoryRule(Rule):
    """Flag a transaction whose merchant category does not appear anywhere in
    the account's earlier transactions.

    Accounts with fewer than `min_history` earlier transactions are never
    flagged, because every category looks new to a young account. It is not
    part of the default batch rule set.
    """

    name = "new_category"

    def __init__(self, min_history: int = 10):
        if min_history < 1:
            raise ValueError("min_history must be at least 1")
        self.min_history = min_history

    def evaluate(self, txn: Transaction, history: Sequence[Transaction]) -> bool:
        if len(history) < self.min_history:
            return False
        return all(h.merchant_category != txn.merchant_category for h in history)
