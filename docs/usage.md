# Usage

All data is synthetic. From the repository root:

```
python -m examples.end_to_end
```

This generates seeded transactions, runs the batch and streaming runners
(and checks they flag the same transactions), then prints precision, recall
and F1 overall and per rule.

## Pipeline in code

```python
from src.generator import generate_transactions
from src.batch import run_batch
from src.evaluation import evaluate

txns = generate_transactions(n_accounts=50, days=30, fraud_account_ratio=0.2, seed=42)
flagged = run_batch(txns)            # or: list(run_stream(sorted_txns))
metrics = evaluate(txns, flagged)    # {"overall": Metrics, "<rule>": Metrics, ...}
```

## Adding a rule

Subclass `src.rules.Rule`, give it a `name` equal to the `fraud_pattern` it
targets, implement `evaluate(txn, history)`, add it to `default_rules()` in
`src/batch/runner.py`, and write a test in `tests/`.
