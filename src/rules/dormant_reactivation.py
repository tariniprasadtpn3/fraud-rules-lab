"""Dormant-account reactivation rule: a purchase after a long quiet spell."""

from __future__ import annotations

from datetime import timedelta
from typing import Sequence

from src.generator import Transaction

from .base import Rule


class DormantReactivationRule(Rule):
    """Flag a transaction that ends a long gap in the account's activity.

    The gap is measured from the account's most recent earlier transaction.
    Accounts with no earlier transactions are never flagged, since there is
    nothing to be dormant from.
    """

    name = "dormant_reactivation"

    def __init__(self, dormant_days: int = 14):
        if dormant_days < 1:
            raise ValueError("dormant_days must be at least 1")
        self.dormant_days = dormant_days

    def evaluate(self, txn: Transaction, history: Sequence[Transaction]) -> bool:
        if not history:
            return False
        gap = txn.timestamp - history[-1].timestamp
        return gap >= timedelta(days=self.dormant_days)
