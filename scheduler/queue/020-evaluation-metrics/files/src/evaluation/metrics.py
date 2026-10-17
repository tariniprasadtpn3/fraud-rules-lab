from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, Iterable, Sequence, Set, Tuple

from src.generator.models import Transaction
from src.rules.base import Flag


@dataclass(frozen=True)
class Metrics:
    precision: float
    recall: float
    flagged: int
    positives: int


def precision_recall(flagged: Set[str], truth: Set[str]) -> Tuple[float, float]:
    """Precision and recall of flagged ids against ground-truth ids.

    Either value is 0.0 when its denominator is empty.
    """
    true_positives = len(flagged & truth)
    precision = true_positives / len(flagged) if flagged else 0.0
    recall = true_positives / len(truth) if truth else 0.0
    return precision, recall


def evaluate(
    transactions: Sequence[Transaction], flags: Iterable[Flag]
) -> Dict[str, Metrics]:
    """Score each rule against the fraud pattern of the same name.

    A rule is judged on the transactions labelled with its own name, plus an
    ``"overall"`` entry that treats any flag against any fraud label.
    """
    truth_by_pattern: Dict[str, Set[str]] = defaultdict(set)
    all_truth: Set[str] = set()
    for txn in transactions:
        if txn.fraud_pattern is not None:
            truth_by_pattern[txn.fraud_pattern].add(txn.txn_id)
            all_truth.add(txn.txn_id)

    flagged_by_rule: Dict[str, Set[str]] = defaultdict(set)
    all_flagged: Set[str] = set()
    for flag in flags:
        flagged_by_rule[flag.rule_name].add(flag.txn_id)
        all_flagged.add(flag.txn_id)

    results: Dict[str, Metrics] = {}
    for name in sorted(set(truth_by_pattern) | set(flagged_by_rule)):
        flagged = flagged_by_rule.get(name, set())
        truth = truth_by_pattern.get(name, set())
        precision, recall = precision_recall(flagged, truth)
        results[name] = Metrics(precision, recall, len(flagged), len(truth))

    precision, recall = precision_recall(all_flagged, all_truth)
    results["overall"] = Metrics(precision, recall, len(all_flagged), len(all_truth))
    return results
