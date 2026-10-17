from __future__ import annotations

from datetime import timedelta
from typing import Sequence

from src.generator.models import Transaction

from .base import Rule, within


class GeoMismatchRule(Rule):
    """Flag a sizeable purchase from a foreign country the account has not used recently.

    A transaction is flagged when it happens outside the account's home
    country, is at least ``min_amount``, and no transaction from that country
    appears in the last ``window``.
    """

    name = "geo_mismatch"

    def __init__(
        self, min_amount: float = 100.0, window: timedelta = timedelta(days=30)
    ):
        self.min_amount = min_amount
        self.window = window
        self.lookback = window

    def evaluate(self, txn: Transaction, history: Sequence[Transaction]) -> bool:
        if txn.country == txn.home_country:
            return False
        if txn.amount < self.min_amount:
            return False
        seen = {t.country for t in within(history, txn.timestamp, self.window)}
        return txn.country not in seen
