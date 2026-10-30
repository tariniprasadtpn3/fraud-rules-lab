"""Idle-gap high-amount rule: a large purchase right after a quiet spell."""

from __future__ import annotations

from datetime import timedelta
from typing import Sequence

from src.generator import Transaction

from .base import Rule


class IdleGapHighAmountRule(Rule):
    """Flag a transaction whose amount is strictly above `threshold` and that
    comes at least `gap_days` after the account's previous transaction.

    A softer, amount-gated cousin of `dormant_reactivation`: a short quiet
    spell alone is normal, but a large purchase after one is suspicious.
    Accounts with no earlier transactions are never flagged.
    """

    name = "idle_gap_high_amount"

    def __init__(self, threshold: float = 500.0, gap_days: int = 5):
        if threshold <= 0:
            raise ValueError("threshold must be positive")
        if gap_days < 1:
            raise ValueError("gap_days must be at least 1")
        self.threshold = threshold
        self.gap_days = gap_days

    def evaluate(self, txn: Transaction, history: Sequence[Transaction]) -> bool:
        if not history or txn.amount <= self.threshold:
            return False
        return txn.timestamp - history[-1].timestamp >= timedelta(days=self.gap_days)
