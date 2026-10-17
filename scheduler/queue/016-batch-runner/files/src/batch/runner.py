from __future__ import annotations

from typing import List, Sequence

from src.generator.models import Transaction
from src.rules.base import Flag, Rule


def run_batch(transactions: Sequence[Transaction], rules: Sequence[Rule]) -> List[Flag]:
    """Apply every rule to every transaction with full per-account history.

    Transactions are processed account by account in (timestamp, txn_id)
    order, so the result does not depend on the order of the input.
    """
    ordered = sorted(
        transactions, key=lambda t: (t.account_id, t.timestamp, t.txn_id)
    )
    flags: List[Flag] = []
    current_account = None
    history: List[Transaction] = []
    for txn in ordered:
        if txn.account_id != current_account:
            current_account = txn.account_id
            history = []
        for rule in rules:
            if rule.evaluate(txn, history):
                flags.append(Flag(txn.txn_id, rule.name))
        history.append(txn)
    return flags
