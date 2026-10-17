from __future__ import annotations

import argparse
from typing import Dict, List, Optional

from src.batch.runner import run_batch
from src.evaluation.metrics import Metrics, evaluate
from src.generator.fraud import inject_fraud
from src.generator.synthetic import generate_transactions
from src.rules.registry import default_rules
from src.stream.runner import run_stream


def format_table(results: Dict[str, Metrics]) -> str:
    header = f"{'rule':<22}{'flagged':>9}{'positives':>11}{'precision':>11}{'recall':>9}"
    lines: List[str] = [header, "-" * len(header)]
    for name, m in results.items():
        lines.append(
            f"{name:<22}{m.flagged:>9}{m.positives:>11}{m.precision:>11.2f}{m.recall:>9.2f}"
        )
    return "\n".join(lines)


def main(argv: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser(description="Run the fraud rules lab end to end.")
    parser.add_argument("--accounts", type=int, default=100)
    parser.add_argument("--days", type=int, default=180)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args(argv)

    txns = inject_fraud(
        generate_transactions(args.accounts, args.days, args.seed), seed=args.seed
    )
    batch = run_batch(txns, default_rules())
    stream = run_stream(txns, default_rules())

    print(f"transactions: {len(txns)}  (injected fraud: {sum(t.is_fraud for t in txns)})")
    print(f"batch flags: {len(batch)}  stream flags: {len(stream)}  "
          f"identical: {set(batch) == set(stream)}")
    print()
    print(format_table(evaluate(txns, batch)))


if __name__ == "__main__":
    main()
