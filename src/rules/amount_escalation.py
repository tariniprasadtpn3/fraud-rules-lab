"""Amount-escalation rule: a run of purchases that each grow noticeably."""

from __future__ import annotations

from typing import Sequence

from src.generator import Transaction

from .base import Rule


class AmountEscalationRule(Rule):
    """Flag a transaction that completes a run of `steps` consecutive
    transactions (including itself) where every amount is at least
    `min_growth` times the one before it.

    Escalating amounts are a classic "probing" pattern: a stolen card is
    tried with a small purchase, then larger ones. Accounts with fewer than
    `steps - 1` earlier transactions are never flagged.
    """

    name = "amount_escalation"

    def __init__(self, steps: int = 3, min_growth: float = 1.3):
        if steps < 2:
            raise ValueError("steps must be at least 2")
        if min_growth <= 1:
            raise ValueError("min_growth must be greater than 1")
        self.steps = steps
        self.min_growth = min_growth

    def evaluate(self, txn: Transaction, history: Sequence[Transaction]) -> bool:
        if len(history) < self.steps - 1:
            return False
        amounts = [h.amount for h in history[-(self.steps - 1):]] + [txn.amount]
        return all(b >= self.min_growth * a for a, b in zip(amounts, amounts[1:]))
