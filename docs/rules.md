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
| `cumulative_spend` | its amount plus the account's earlier spend within `window` is strictly above `limit` | `limit=10000.0`, `window=24 hours` | total spend in the window is at or below `limit`; needs no history; not in the default batch set |
| `country_hop` | the previous transaction of the same account was in a different country and is at most `window` older | `window=2 hours` | same country as the previous transaction, or the gap exceeds the window; needs no history |
| `category_burst` | counting itself, the account used at least `min_categories` distinct merchant categories within `window` | `min_categories=4`, `window=1 hour` | fewer distinct categories in the window; needs no history; not in the default batch set |
| `new_country` | its country never appears in the account's earlier transactions | `min_history=5` | the account has fewer than `min_history` earlier transactions or the country was used before; not in the default batch set |
| `new_max_amount` | its amount exceeds `factor` times the largest earlier amount of the account | `factor=1.5`, `min_history=5` | the account has fewer than `min_history` earlier transactions or the amount is within the limit; not in the default batch set |
| `amount_escalation` | the last `steps` amounts (including this one) each grow by at least `min_growth` times | `steps=3`, `min_growth=1.3` | fewer than `steps - 1` earlier transactions or growth too small; not in the default batch set |
| `amount_zscore` | its amount is more than `threshold` standard deviations above the mean of the account's earlier amounts | `threshold=3.0`, `min_history=10` | the account has fewer than `min_history` earlier transactions or its earlier amounts all equal; not in the default batch set |
| `weekend_high_amount` | it happens on a Saturday or Sunday and its amount is at least `threshold` | `threshold=500.0` | weekday, or amount below `threshold`; needs no history; not in the default batch set |
| `foreign_high_amount` | its country differs from the account's most common country and its amount is at least `threshold` | `threshold=300.0`, `min_history=5` | the account has fewer than `min_history` earlier transactions, amount below `threshold`, or home country; not in the default batch set |
| `rapid_succession` | it occurs at most `max_gap` after the account's previous transaction | `max_gap=10 seconds` | longer gap, out-of-order timestamps or no earlier transaction; not in the default batch set |
| `new_hour` | its hour of day never appears in the account's earlier transactions | `min_history=10` | the account has fewer than `min_history` earlier transactions or the hour was used before; not in the default batch set |
| `new_account_high_amount` | its amount is at least `threshold` and the account has fewer than `max_history` earlier transactions | `threshold=1000.0`, `max_history=3` | the account is established or the amount is below `threshold`; not in the default batch set |
| `category_max_amount` | its amount exceeds `factor` times the largest earlier amount in the same category for the account | `factor=2.0`, `min_history=3` | fewer than `min_history` earlier transactions in that category or amount within `factor` of the max; not in the default batch set |
| `new_country_high_amount` | its amount is at least `threshold` and its country never appears in the account's earlier transactions | `threshold=300.0`, `min_history=5` | the account has fewer than `min_history` earlier transactions, amount below `threshold`, or the country was used before; not in the default batch set |
| `new_category_high_amount` | its amount is at least `threshold` and its merchant category never appears in the account's earlier transactions | `threshold=300.0`, `min_history=10` | the account has fewer than `min_history` earlier transactions, amount below `threshold`, or the category was used before; not in the default batch set |
| `new_hour_high_amount` | its amount is at least `threshold` and its hour of day never appears in the account's earlier transactions | `threshold=300.0`, `min_history=10` | amount below `threshold` or the account has fewer than `min_history` earlier transactions; not in the default batch set |
| `new_weekday_high_amount` | its amount is at least `threshold` and its day of the week never appears in the account's earlier transactions | `threshold=300.0`, `min_history=14` | amount below `threshold` or the account has fewer than `min_history` earlier transactions; not in the default batch set |
| `night_high_amount` | its amount is at least `threshold` and its hour falls in `[start_hour, end_hour)` (may wrap past midnight) | `threshold=300.0`, `start_hour=1`, `end_hour=5` | amount below `threshold` or hour outside the window; needs no history; not in the default batch set |

Ten of the twenty-seven rules are in `default_rules()`: the four core rules plus `high_amount`, `night_hours`, `round_amount`, `new_category`, `repeat_amount` and `country_hop`. Every other rule in the table is opt-in: import it from `src.rules` and pass an instance in `rules=`, for example `run_batch(txns, rules=core_rules() + [NewHourHighAmountRule(), CardTestingRule()])`. `core_rules()` returns just the first four.

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
