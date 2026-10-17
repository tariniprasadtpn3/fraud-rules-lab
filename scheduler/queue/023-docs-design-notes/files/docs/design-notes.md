# Design notes

## One rule contract for both execution styles

A rule implements a single method:

```python
def evaluate(self, txn: Transaction, history: Sequence[Transaction]) -> bool
```

`history` is the *earlier* transactions of the same account, oldest first. The
batch runner builds it from the full dataset; the streaming runner builds it
from bounded per-account state. Because the rule only sees `history`, the same
code runs in both modes and the two runners can be compared directly.

## Why a rule declares `lookback`

Streaming state has to be bounded. Each rule states how far back it needs to
look (`lookback`), and the stream processor keeps the maximum of those across
the active rules. Rules filter `history` to their own window with
`within(...)`, so extra history never changes a result.

Dormancy is the special case: it needs the *latest* earlier transaction however
old it is. The stream processor therefore always keeps the most recent
transaction per account, even past the retention window.

## Why batch and streaming results are identical

- Both runners order transactions by `(timestamp, txn_id)`, so ties break the
  same way.
- Evicted streaming state is always older than every future rule window, so
  eviction can never remove something a rule would have used.
- `tests/test_stream_runner.py` checks the equality on a synthetic dataset with
  injected fraud.

## Evaluation

Each rule is scored against the injected fraud pattern with the same name
(precision and recall), plus an `overall` row. A transaction flagged by a rule
for a *different* pattern counts as a false positive for that rule, which makes
overlap between rules visible instead of hiding it.

## Known simplifications

- Synthetic data only, one currency, fixed thresholds chosen for readability.
- No late or out-of-order events in the streaming runner; input is processed in
  event-time order.
- Per-account state lives in memory; a real pipeline would use keyed,
  fault-tolerant state.
