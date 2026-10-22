"""Night-hours rule: activity during unusual overnight hours."""

from __future__ import annotations

from typing import Sequence

from src.generator import Transaction

from .base import Rule


class NightHoursRule(Rule):
    """Flag a transaction whose hour of day falls in [`start_hour`, `end_hour`).

    The window may wrap past midnight (for example 23 to 5). It needs no
    history.
    """

    name = "night_hours"

    def __init__(self, start_hour: int = 1, end_hour: int = 5):
        if not (0 <= start_hour <= 23 and 0 <= end_hour <= 23):
            raise ValueError("hours must be between 0 and 23")
        if start_hour == end_hour:
            raise ValueError("start_hour and end_hour must differ")
        self.start_hour = start_hour
        self.end_hour = end_hour

    def evaluate(self, txn: Transaction, history: Sequence[Transaction]) -> bool:
        hour = txn.timestamp.hour
        if self.start_hour < self.end_hour:
            return self.start_hour <= hour < self.end_hour
        return hour >= self.start_hour or hour < self.end_hour
