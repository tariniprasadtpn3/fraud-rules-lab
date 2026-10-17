# fraud-rules-lab

A small, learning-focused lab for building a **fraud-detection rule engine** on
**synthetic transaction data**. Each rule is implemented in a batch style and a
streaming style so the two approaches can be compared side by side.

> All data in this repository is synthetic and all rules are generic,
> textbook examples. Nothing here comes from any employer or client.

## Goals

- Build a clean, testable rule interface for transaction-level fraud checks.
- Generate reproducible synthetic transactions (fixed seed) with injected fraud patterns.
- Implement common rules, such as velocity, amount spikes, geo mismatch and
  dormant-account reactivation, one at a time with unit tests.
- Compare batch and streaming-style execution of the same rules.
- Measure rule quality with precision and recall on the injected patterns.

## Layout

```
fraud-rules-lab/
├── src/
│   ├── generator/   # synthetic transactions and fraud injection
│   ├── rules/       # rule interface and the four rules
│   ├── batch/       # batch runner
│   ├── stream/      # streaming-style runner
│   ├── evaluation/  # precision and recall
│   └── cli.py       # end-to-end demo
├── tests/           # unit tests, one module per component
└── docs/            # design notes and an example run
```

## Quick start

```bash
pip install -r requirements-dev.txt
python -m pytest
python -m src.cli --accounts 100 --days 180 --seed 42
```

See [docs/example-run.md](docs/example-run.md) for sample output and what it
shows, and [docs/design-notes.md](docs/design-notes.md) for the design.

## Rules

| Rule | Flags a transaction when... |
|------|-----------------------------|
| `velocity` | it pushes an account over N transactions inside a short window |
| `amount_spike` | the amount is several times the recent average |
| `geo_mismatch` | it is a sizeable purchase from a new foreign country |
| `dormant_reactivation` | it is a sizeable purchase after a long silence |

## Roadmap

- [x] Synthetic transaction generator with a fixed seed
- [x] Rule interface plus first rule, with tests
- [x] More rules, one at a time
- [x] Batch runner that applies all rules and outputs flagged transactions
- [x] Streaming-style runner
- [x] Evaluation metrics (precision and recall)
- [x] Docs and examples
- [ ] Tunable thresholds and a threshold sweep
- [ ] Per-account adaptive amount thresholds
