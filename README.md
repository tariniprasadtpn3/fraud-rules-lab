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

## Planned layout

```
fraud-rules-lab/
├── src/
│   ├── generator/   # synthetic transaction generator
│   ├── rules/       # rule interface and individual rules
│   ├── batch/       # batch runner
│   └── stream/      # streaming-style runner
├── tests/           # unit tests, one module per rule
└── docs/            # design notes and examples
```

## Status

Early stage. The synthetic transaction generator (`src/generator`, see
`docs/generator.md`) and the rule interface with the rules velocity, amount
spike, geo mismatch and dormant-account reactivation (`src/rules`), are done. Other folders are added as the corresponding code
lands.

## Roadmap

1. [x] Synthetic transaction generator with a fixed seed
2. [x] Rule interface plus first rule (velocity), with tests
3. [x] More rules, one at a time (amount spike, geo mismatch, dormant-account reactivation)
4. [ ] Batch runner that applies all rules and outputs flagged transactions
5. [ ] Streaming-style runner
6. [ ] Evaluation metrics (precision and recall)
7. [ ] Docs and examples

## Running the tests

```
pip install pytest
pytest
```
