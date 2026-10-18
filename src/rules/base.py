"""Rule interface shared by every fraud rule.

A rule looks at one transaction plus that account's *earlier* transactions
and decides whether to flag it. Because a rule never sees the future, the
same code can later be driven by a batch runner or a streaming runner.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Sequence

from src.generator import Transaction


class Rule(ABC):
    """Base class for a single fraud rule."""

    #: Short identifier used when reporting which rule flagged a transaction.
    name: str = "rule"

    @abstractmethod
    def evaluate(self, txn: Transaction, history: Sequence[Transaction]) -> bool:
        """Return True if `txn` should be flagged.

        `history` holds the same account's earlier transactions, oldest
        first. It never includes `txn` itself.
        """
