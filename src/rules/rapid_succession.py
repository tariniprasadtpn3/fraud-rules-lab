"""Rapid-succession rule: two purchases on one account seconds apart."""

from __future__ import annotations

from datetime import timedelta
from typing import Sequence

from src.generator import Transaction

from .base import Rule


class RapidSuccessionRule(Rule):
    """Flag a transaction made at most `max_gap` after the account's
    immediately preceding transaction (a human rarely pays twice within
    seconds, so this hints at scripted use). It needs no minimum history.
    """

    name = "rapid_succession"

    def __init__(self, max_gap: timedelta = timedelta(seconds=10)):
        if max_gap <= timedelta(0):
            raise ValueError("max_gap must be positive")
        self.max_gap = max_gap

    def evaluate(self, txn: Transaction, history: Sequence[Transaction]) -> bool:
        if not history:
            return False
        gap = txn.timestamp - history[-1].timestamp
        return timedelta(0) <= gap <= self.max_gap
