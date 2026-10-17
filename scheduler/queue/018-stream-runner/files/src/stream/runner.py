from __future__ import annotations

from collections import defaultdict, deque
from typing import Deque, Dict, List, Sequence

from src.generator.models import Transaction
from src.rules.base import Flag, Rule


class StreamProcessor:
    """Process transactions one at a time, keeping only bounded history.

    Per account it retains transactions newer than the longest rule
    ``lookback`` plus the most recent one regardless of age (dormancy rules
    need it). Rules see the same ``history`` contract as in the batch runner.
    """

    def __init__(self, rules: Sequence[Rule]):
        self.rules = list(rules)
        self.retention = max(rule.lookback for rule in self.rules)
        self._state: Dict[str, Deque[Transaction]] = defaultdict(deque)

    def process(self, txn: Transaction) -> List[Flag]:
        window = self._state[txn.account_id]
        history = list(window)
        flags = [
            Flag(txn.txn_id, rule.name)
            for rule in self.rules
            if rule.evaluate(txn, history)
        ]
        window.append(txn)
        self._evict(window, txn)
        return flags

    def state_size(self, account_id: str) -> int:
        """Number of transactions currently retained for an account."""
        return len(self._state.get(account_id, ()))

    def _evict(self, window: Deque[Transaction], newest: Transaction) -> None:
        cutoff = newest.timestamp - self.retention
        while len(window) > 1 and window[0].timestamp < cutoff:
            window.popleft()


def run_stream(transactions: Sequence[Transaction], rules: Sequence[Rule]) -> List[Flag]:
    """Feed transactions through a StreamProcessor in event-time order."""
    processor = StreamProcessor(rules)
    flags: List[Flag] = []
    for txn in sorted(transactions, key=lambda t: (t.timestamp, t.txn_id)):
        flags.extend(processor.process(txn))
    return flags
