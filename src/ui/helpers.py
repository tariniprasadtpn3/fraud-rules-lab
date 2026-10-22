"""UI-independent helpers behind the Streamlit app (no streamlit import here).

Keeping the logic here means it can be unit tested without a browser.
All data is synthetic.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Sequence

import pandas as pd

from src.batch import FlaggedTransaction, default_rules, run_batch
from src.evaluation import Metrics, evaluate
from src.generator import Transaction, generate_transactions


@dataclass(frozen=True)
class RunResult:
    """Everything the UI shows for one run."""

    transactions: List[Transaction]
    flagged: List[FlaggedTransaction]
    metrics: Dict[str, Metrics]


def available_rules() -> List[str]:
    """Names of every rule in the default set, in order."""
    return [r.name for r in default_rules()]


def run_pipeline(
    n_accounts: int = 50,
    days: int = 30,
    fraud_account_ratio: float = 0.2,
    seed: int = 42,
    rule_names: Sequence[str] | None = None,
    min_rules: int = 1,
) -> RunResult:
    """Generate seeded data, run the selected rules in batch and evaluate."""
    rules = [r for r in default_rules() if rule_names is None or r.name in rule_names]
    if not rules:
        raise ValueError("select at least one rule")
    txns = generate_transactions(n_accounts, days, fraud_account_ratio, seed)
    flagged = run_batch(txns, rules, min_rules=min_rules)
    return RunResult(txns, flagged, evaluate(txns, flagged))


def flagged_frame(flagged: Sequence[FlaggedTransaction]) -> pd.DataFrame:
    """One row per flagged transaction, with the rules joined by '|' and the true label."""
    columns = ["txn_id", "account_id", "timestamp", "amount", "country",
               "merchant_category", "rules", "is_fraud", "fraud_pattern"]
    rows = [
        [f.txn.txn_id, f.txn.account_id, f.txn.timestamp, f.txn.amount, f.txn.country,
         f.txn.merchant_category, "|".join(f.rules), f.txn.is_fraud, f.txn.fraud_pattern or ""]
        for f in flagged
    ]
    return pd.DataFrame(rows, columns=columns)


def metrics_frame(metrics: Dict[str, Metrics]) -> pd.DataFrame:
    """Metrics as a table indexed by rule name ('overall' first)."""
    rows = [
        [name, m.tp, m.fp, m.fn, m.precision, m.recall, m.f1]
        for name, m in metrics.items()
    ]
    return pd.DataFrame(rows, columns=["rule", "tp", "fp", "fn", "precision", "recall", "f1"]).set_index("rule")
