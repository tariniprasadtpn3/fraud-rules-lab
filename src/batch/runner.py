"""Batch runner: apply every rule to a full list of transactions at once.

Transactions are grouped per account and replayed in time order, so each rule
only ever sees that account's earlier transactions (never the future). The
output lists each flagged transaction with the names of the rules that fired.
"""

from __future__ import annotations

import csv
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

from src.generator import Transaction
from src.rules import (
    AmountSpikeRule,
    CountryHopRule,
    DormantReactivationRule,
    GeoMismatchRule,
    HighAmountRule,
    NewCategoryRule,
    NightHoursRule,
    RepeatAmountRule,
    RoundAmountRule,
    Rule,
    VelocityRule,
)


@dataclass(frozen=True)
class FlaggedTransaction:
    """A transaction together with the names of the rules that flagged it."""

    txn: Transaction
    rules: Tuple[str, ...]


def core_rules() -> List[Rule]:
    """Return only the four original rules (velocity, amount spike, geo mismatch, dormant)."""
    return [VelocityRule(), AmountSpikeRule(), GeoMismatchRule(), DormantReactivationRule()]


def default_rules() -> List[Rule]:
    """Return one instance of every rule with its default settings."""
    return core_rules() + [
        HighAmountRule(),
        NightHoursRule(),
        RoundAmountRule(),
        NewCategoryRule(),
        RepeatAmountRule(),
        CountryHopRule(),
    ]


def run_batch(
    transactions: Iterable[Transaction], rules: Sequence[Rule] | None = None
) -> List[FlaggedTransaction]:
    """Apply `rules` to `transactions` and return the flagged ones in time order."""
    active = list(rules) if rules is not None else default_rules()
    ordered = sorted(transactions, key=lambda t: (t.timestamp, t.txn_id))

    history: Dict[str, List[Transaction]] = defaultdict(list)
    flagged: List[FlaggedTransaction] = []
    for txn in ordered:
        past = history[txn.account_id]
        fired = tuple(rule.name for rule in active if rule.evaluate(txn, past))
        if fired:
            flagged.append(FlaggedTransaction(txn, fired))
        past.append(txn)
    return flagged


def write_flagged_csv(flagged: Iterable[FlaggedTransaction], path: Path | str) -> None:
    """Write flagged transactions to a CSV file, one row per transaction."""
    with open(path, "w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["txn_id", "account_id", "timestamp", "amount", "country", "rules"])
        for f in flagged:
            t = f.txn
            writer.writerow(
                [t.txn_id, t.account_id, t.timestamp.isoformat(), t.amount, t.country, "|".join(f.rules)]
            )
