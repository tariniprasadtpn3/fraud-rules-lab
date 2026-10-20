"""Precision and recall of flagged transactions against ground-truth labels.

Scores are computed overall (any rule fired vs `is_fraud`) and per rule. A rule
is scored against the fraud transactions of its own injected pattern, so it is
not penalised in recall for missing another rule's pattern.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Set

from src.batch import FlaggedTransaction
from src.generator import Transaction


@dataclass(frozen=True)
class Metrics:
    """Confusion counts with derived precision, recall and F1."""

    tp: int
    fp: int
    fn: int

    @property
    def precision(self) -> float:
        return self.tp / (self.tp + self.fp) if (self.tp + self.fp) else 0.0

    @property
    def recall(self) -> float:
        return self.tp / (self.tp + self.fn) if (self.tp + self.fn) else 0.0

    @property
    def f1(self) -> float:
        p, r = self.precision, self.recall
        return 2 * p * r / (p + r) if (p + r) else 0.0


def _score(flagged_ids: Set[str], positive_ids: Set[str]) -> Metrics:
    tp = len(flagged_ids & positive_ids)
    return Metrics(tp=tp, fp=len(flagged_ids - positive_ids), fn=len(positive_ids - flagged_ids))


def evaluate(
    transactions: Iterable[Transaction], flagged: Iterable[FlaggedTransaction]
) -> Dict[str, Metrics]:
    """Return metrics under key "overall" plus one entry per rule name.

    Per-rule positives are the fraud transactions whose `fraud_pattern` equals
    the rule name; per-rule false positives are that rule's flags on
    transactions outside that pattern.
    """
    txns = list(transactions)
    fraud_ids = {t.txn_id for t in txns if t.is_fraud}
    flagged = list(flagged)

    result = {"overall": _score({f.txn.txn_id for f in flagged}, fraud_ids)}

    rule_names = {r for f in flagged for r in f.rules} | {
        t.fraud_pattern for t in txns if t.fraud_pattern
    }
    for name in sorted(rule_names):
        positives = {t.txn_id for t in txns if t.is_fraud and t.fraud_pattern == name}
        hits = {f.txn.txn_id for f in flagged if name in f.rules}
        result[name] = _score(hits, positives)
    return result
