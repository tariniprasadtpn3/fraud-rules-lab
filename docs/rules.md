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
| `high_amount` | its amount is strictly above `threshold` | `threshold=5000.0` | never; needs no history |
| `night_hours` | its hour of day is in `[start_hour, end_hour)`, wrapping past midnight if `start_hour > end_hour` | `start_hour=1`, `end_hour=5` | never; needs no history |
| `round_amount` | its amount is at least `min_amount` and an exact multiple of `step` | `step=500.0`, `min_amount=1000.0` | the amount is below `min_amount` or not a multiple of `step`; needs no history |
| `new_category` | its merchant category never appears in the account's earlier transactions | `min_history=10` | the account has fewer than `min_history` earlier transactions or the category was used before |
| `repeat_amount` | an earlier transaction of the same account has exactly the same amount and is at most `window` older | `window=10 minutes` | no earlier same-amount transaction falls inside the window; needs no history |
| `card_testing` | amount is at most `max_amount` and at least `min_count - 1` earlier transactions of at most `max_amount` fall inside `window` | `max_amount=5.0`, `min_count=3`, `window=10 minutes` | fewer small transactions in the window, or the current amount is above `max_amount`; not in the default batch set |
| `country_hop` | the previous transaction of the same account was in a different country and is at most `window` older | `window=2 hours` | same country as the previous transaction, or the gap exceeds the window; needs no history |

Ten of the eleven rules are in `default_rules()` (`card_testing` is opt-in: pass `CardTestingRule()` in `rules=`); `core_rules()` returns just the first four.

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
