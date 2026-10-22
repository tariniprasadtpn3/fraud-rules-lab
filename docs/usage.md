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

## Requiring several rules to agree

All ten rules run by default, and the noisy ones (`high_amount`, `night_hours`)
lower overall precision. Pass `min_rules` to `run_batch`, `run_stream` or
`StreamProcessor` to report a transaction only when at least that many rules
fire on it:

```python
flagged = run_batch(txns, min_rules=2)
```

Use `core_rules()` for just the original four rules. Compare settings with
`evaluate` to see the precision/recall trade-off.

See `docs/rules.md` for each rule's parameters and defaults.

## Adding a rule

Subclass `src.rules.Rule`, give it a `name` equal to the `fraud_pattern` it
targets, implement `evaluate(txn, history)`, add it to `default_rules()` in
`src/batch/runner.py`, and write a test in `tests/`.
