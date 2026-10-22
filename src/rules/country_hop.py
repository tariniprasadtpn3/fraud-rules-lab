"""Country-hop rule: a country change shortly after the previous transaction."""

from __future__ import annotations

from datetime import timedelta
from typing import Sequence

from src.generator import Transaction

from .base import Rule


class CountryHopRule(Rule):
    """Flag a transaction made in a different country than the account's
    immediately preceding transaction, when the two are at most `window` apart
    (physically implausible travel, a generic "impossible travel" check).

    It needs no minimum history.
    """

    name = "country_hop"

    def __init__(self, window: timedelta = timedelta(hours=2)):
        if window <= timedelta(0):
            raise ValueError("window must be positive")
        self.window = window

    def evaluate(self, txn: Transaction, history: Sequence[Transaction]) -> bool:
        if not history:
            return False
        prev = history[-1]
        gap = txn.timestamp - prev.timestamp
        return prev.country != txn.country and timedelta(0) <= gap <= self.window
