# Synthetic transaction generator

`src/generator` produces reproducible, fully synthetic card transactions with
injected fraud patterns and ground-truth labels, so rules can later be scored
with precision and recall.

## Usage

```python
from src.generator import generate_transactions, write_csv

txns = generate_transactions(n_accounts=50, days=30, fraud_account_ratio=0.2, seed=42)
write_csv(txns, "data/transactions.csv")
```

The same arguments always give the same output.

## Fields

| Field | Meaning |
|---|---|
| `txn_id` | Sequential id, assigned after sorting by time |
| `account_id` | Synthetic account, `ACC0001` and up |
| `timestamp` | Transaction time |
| `amount` | Amount in a single synthetic currency |
| `merchant_category` | One of a small fixed set |
| `country` | Two-letter country code |
| `is_fraud` | Ground-truth label |
| `fraud_pattern` | Injected pattern name, or empty for normal traffic |

## Injected patterns

Selected accounts each receive exactly one pattern, cycling through the list.

| Pattern | What is injected |
|---|---|
| `velocity` | Six small purchases within four minutes |
| `amount_spike` | One purchase 15-30x the account's typical amount |
| `geo_mismatch` | One purchase in a country other than the account's home |
| `dormant_reactivation` | A large purchase on the last day after weeks of silence |

Normal traffic stays in the account's home country and within 0.3-1.7x its
typical amount, so each pattern is a clean signal for the matching rule.
