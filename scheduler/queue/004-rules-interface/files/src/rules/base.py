from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Sequence

from src.generator.models import Transaction


@dataclass(frozen=True)
class Flag:
    """A rule firing on a transaction."""

    txn_id: str
    rule_name: str


class Rule(ABC):
    """A fraud rule evaluated for one transaction at a time.

    ``history`` holds the *earlier* transactions of the same account in time
    order. Batch and streaming runners differ only in how they build that
    history, so the same rule can run in both modes unchanged.

    ``lookback`` tells a streaming runner how much history it must retain. A
    rule that needs the most recent earlier transaction (however old) relies
    on runners always keeping the latest one.
    """

    name: str = "rule"
    lookback: timedelta = timedelta(days=30)

    @abstractmethod
    def evaluate(self, txn: Transaction, history: Sequence[Transaction]) -> bool:
        """Return True if ``txn`` should be flagged."""


def within(
    history: Sequence[Transaction], now: datetime, window: timedelta
) -> List[Transaction]:
    """Return the history entries that fall inside ``[now - window, now]``."""
    cutoff = now - window
    return [t for t in history if t.timestamp >= cutoff]
