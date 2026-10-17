from __future__ import annotations

from datetime import timedelta
from typing import Sequence

from src.generator.models import Transaction

from .base import Rule


class DormantReactivationRule(Rule):
    """Flag a sizeable transaction after a long silence on the account.

    Only the most recent earlier transaction matters, so runners must always
    keep the latest transaction per account even when it is older than the
    rule's ``lookback``. Accounts with no history are new, not dormant.
    """

    name = "dormant_reactivation"

    def __init__(self, dormant_days: int = 90, min_amount: float = 100.0):
        self.dormant_period = timedelta(days=dormant_days)
        self.min_amount = min_amount
        self.lookback = self.dormant_period

    def evaluate(self, txn: Transaction, history: Sequence[Transaction]) -> bool:
        if not history or txn.amount < self.min_amount:
            return False
        gap = txn.timestamp - history[-1].timestamp
        return gap >= self.dormant_period
