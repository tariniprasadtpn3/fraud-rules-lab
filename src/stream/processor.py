"""Streaming-style runner: score transactions one at a time, as they arrive.

Unlike the batch runner, nothing is sorted or grouped up front. The processor
keeps only per-account history and returns a verdict for each transaction
immediately. Fed in time order, it flags exactly what the batch runner flags.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, Iterable, Iterator, List, Optional, Sequence

from src.batch.runner import FlaggedTransaction, default_rules
from src.generator import Transaction
from src.rules import Rule


class StreamProcessor:
    """Stateful processor: call `process` once per incoming transaction."""

    def __init__(self, rules: Sequence[Rule] | None = None, max_history: Optional[int] = None):
        self.rules = list(rules) if rules is not None else default_rules()
        self.max_history = max_history  # None keeps the full per-account history
        self._history: Dict[str, List[Transaction]] = defaultdict(list)

    def process(self, txn: Transaction) -> Optional[FlaggedTransaction]:
        """Evaluate `txn` against the account's earlier transactions."""
        past = self._history[txn.account_id]
        fired = tuple(rule.name for rule in self.rules if rule.evaluate(txn, past))
        past.append(txn)
        if self.max_history is not None and len(past) > self.max_history:
            del past[: len(past) - self.max_history]
        return FlaggedTransaction(txn, fired) if fired else None


def run_stream(
    transactions: Iterable[Transaction], rules: Sequence[Rule] | None = None
) -> Iterator[FlaggedTransaction]:
    """Lazily yield flagged transactions from an (assumed time-ordered) stream."""
    processor = StreamProcessor(rules)
    for txn in transactions:
        result = processor.process(txn)
        if result is not None:
            yield result
