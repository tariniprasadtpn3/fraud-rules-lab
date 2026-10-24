"""New-country rule: a purchase in a country the account has never used before."""

from __future__ import annotations

from typing import Sequence

from src.generator import Transaction

from .base import Rule


class NewCountryRule(Rule):
    """Flag a transaction whose country never appears in the account's earlier
    transactions.

    Unlike `geo_mismatch` (compares with the most common country), this fires
    on any country not seen before, so a second visit to the same foreign
    country is not flagged. Accounts with fewer than `min_history` earlier
    transactions are never flagged.
    """

    name = "new_country"

    def __init__(self, min_history: int = 5):
        if min_history < 1:
            raise ValueError("min_history must be at least 1")
        self.min_history = min_history

    def evaluate(self, txn: Transaction, history: Sequence[Transaction]) -> bool:
        if len(history) < self.min_history:
            return False
        return all(h.country != txn.country for h in history)
