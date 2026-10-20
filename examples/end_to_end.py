"""End-to-end demo: generate synthetic data, run batch and stream, evaluate.

Run from the repository root:  python -m examples.end_to_end
"""

from __future__ import annotations

from typing import Dict

from src.batch import run_batch
from src.evaluation import Metrics, evaluate
from src.generator import generate_transactions
from src.stream import run_stream


def run_demo(seed: int = 42) -> Dict[str, Metrics]:
    """Run the full pipeline on seeded synthetic data and return the metrics."""
    txns = generate_transactions(n_accounts=50, days=30, fraud_account_ratio=0.2, seed=seed)
    batch = run_batch(txns)
    stream = list(run_stream(sorted(txns, key=lambda t: (t.timestamp, t.txn_id))))
    if [f.txn.txn_id for f in batch] != [f.txn.txn_id for f in stream]:
        raise RuntimeError("batch and stream runners disagree")
    return evaluate(txns, batch)


def main() -> None:
    metrics = run_demo()
    print(f"{'rule':<24}{'precision':>10}{'recall':>8}{'f1':>8}")
    for name, m in metrics.items():
        print(f"{name:<24}{m.precision:>10.2f}{m.recall:>8.2f}{m.f1:>8.2f}")


if __name__ == "__main__":
    main()
