# Example run

```bash
python -m src.cli            # 100 accounts, 180 days, seed 42
```

Output (Python 3.13; exact numbers can shift slightly on other versions):

```
transactions: 14485  (injected fraud: 52)
batch flags: 45  stream flags: 45  identical: True

rule                    flagged  positives  precision   recall
--------------------------------------------------------------
amount_spike                 13          5       0.38     1.00
dormant_reactivation          2          2       1.00     1.00
geo_mismatch                  5          5       1.00     1.00
velocity                     25         40       1.00     0.62
overall                      44         52       0.84     0.71
```

## What it shows

- **Batch and streaming agree.** Both runners produce the same 45 flags.
- **Velocity trades recall for precision.** It can only fire once the threshold
  is crossed, so the first transactions of every burst are missed by design.
  Lowering `max_txns` catches more of each burst at the cost of more false alarms
  on busy but legitimate accounts.
- **Amount spike has a precision problem.** Of its 8 false positives, 7 are
  legitimate purchases that were simply much larger than the account's recent
  average, and 1 is the injected geo-mismatch purchase, which is also large. A
  percentile-based or per-account-variance threshold is the natural next step.
- **Geo mismatch and dormant reactivation are clean here**, partly because the
  synthetic data never has legitimate foreign spending or long silences.
  Real data would not be this kind.

To reproduce a different scenario, change `--accounts`, `--days` or `--seed`.
