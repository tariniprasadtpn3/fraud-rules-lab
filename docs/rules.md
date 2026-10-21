# Rules reference

Every rule subclasses `src.rules.Rule` and implements
`evaluate(txn, history) -> bool`. `history` holds the same account's earlier
transactions, oldest first, and never includes `txn`, so the same rule works
in the batch and streaming runners. All data is synthetic.

| Rule (`name`) | Flags a transaction when... | Parameters (defaults) | Never flags when... |
|---|---|---|---|
| `velocity` | it is the `min_count`-th or later transaction inside `window`, counting itself | `min_count=3`, `window=5 minutes` | fewer than `min_count` transactions fall in the window |
| `amount_spike` | its amount is more than `multiplier` times the account's average earlier amount | `multiplier=4.0`, `min_history=5` | the account has fewer than `min_history` earlier transactions |
| `geo_mismatch` | its country differs from the account's most common earlier country | `min_history=5` | the account has fewer than `min_history` earlier transactions |
| `dormant_reactivation` | the gap since the account's previous transaction is at least `dormant_days` | `dormant_days=14` | the account has no earlier transactions |
| `high_amount` | its amount is strictly above `threshold` (not in the default batch rule set) | `threshold=5000.0` | never; needs no history |
| `night_hours` | its hour of day is in `[start_hour, end_hour)`, wrapping past midnight if `start_hour > end_hour` (not in the default batch rule set) | `start_hour=1`, `end_hour=5` | never; needs no history |

Constructors raise `ValueError` for out-of-range parameters (for example
`multiplier <= 1` or `min_count < 2`).

## Tuning example

```python
from datetime import timedelta
from src.batch import run_batch
from src.rules import AmountSpikeRule, VelocityRule

flagged = run_batch(txns, rules=[
    VelocityRule(min_count=4, window=timedelta(minutes=10)),
    AmountSpikeRule(multiplier=6.0),
])
```

Compare settings with `src.evaluation.evaluate` to see the precision/recall
trade-off of each threshold.
