"""Geo mismatch rule: a purchase outside the account's usual country."""

from __future__ import annotations

from collections import Counter
from typing import Sequence

from src.generator import Transaction

from .base import Rule


class GeoMismatchRule(Rule):
    """Flag a transaction made in a country other than the account's usual one.

    The usual ("home") country is the most common country in the account's
    earlier transactions. Accounts with fewer than `min_history` earlier
    transactions are never flagged, because home cannot be established yet.
    """

    name = "geo_mismatch"

    def __init__(self, min_history: int = 5):
        if min_history < 1:
            raise ValueError("min_history must be at least 1")
        self.min_history = min_history

    def evaluate(self, txn: Transaction, history: Sequence[Transaction]) -> bool:
        if len(history) < self.min_history:
            return False
        # most_common breaks ties by first occurrence, so the result is deterministic.
        home = Counter(h.country for h in history).most_common(1)[0][0]
        return txn.country != home
