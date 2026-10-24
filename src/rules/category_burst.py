"""Category-burst rule: many distinct merchant categories in a short window."""

from __future__ import annotations

from datetime import timedelta
from typing import Sequence

from src.generator import Transaction

from .base import Rule


class CategoryBurstRule(Rule):
    """Flag a transaction when, counting itself, the account has used at least
    `min_categories` distinct merchant categories within `window`.

    A stolen card is often used to sample several kinds of merchant quickly.
    It needs no minimum history.
    """

    name = "category_burst"

    def __init__(self, min_categories: int = 4, window: timedelta = timedelta(hours=1)):
        if min_categories < 2:
            raise ValueError("min_categories must be at least 2")
        if window <= timedelta(0):
            raise ValueError("window must be positive")
        self.min_categories = min_categories
        self.window = window

    def evaluate(self, txn: Transaction, history: Sequence[Transaction]) -> bool:
        categories = {txn.merchant_category}
        for h in history:
            if timedelta(0) <= txn.timestamp - h.timestamp <= self.window:
                categories.add(h.merchant_category)
        return len(categories) >= self.min_categories
