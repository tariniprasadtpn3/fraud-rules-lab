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

All roadmap steps are done (extra generic rules `high_amount`, `night_hours`, `round_amount`, `new_category`, `repeat_amount` and `country_hop` are also available and part of the default batch rule set, while `card_testing`, `cumulative_spend` and `category_burst` are available as opt-in rules; `core_rules()` keeps the original four); see `docs/usage.md` and run `python -m examples.end_to_end` for a demo. The synthetic transaction generator (`src/generator`, see
`docs/generator.md`) and the rule interface with the rules velocity, amount
spike, geo mismatch and dormant-account reactivation (`src/rules`), the batch runner (`src/batch`, `run_batch`) and the streaming-style runner (`src/stream`, `StreamProcessor`, `run_stream`) and the evaluation metrics (`src/evaluation`, `evaluate`: overall and per-rule precision, recall and F1) are done. Other folders are added as the corresponding code
lands.

## Roadmap

1. [x] Synthetic transaction generator with a fixed seed
2. [x] Rule interface plus first rule (velocity), with tests
3. [x] More rules, one at a time (amount spike, geo mismatch, dormant-account reactivation)
4. [x] Batch runner that applies all rules and outputs flagged transactions
5. [x] Streaming-style runner
6. [x] Evaluation metrics (precision and recall)
7. [x] Docs and examples (`docs/usage.md`, `examples/end_to_end.py`)

## Streamlit UI

```
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Pick the seed, data size, active rules and the minimum number of rules that
must agree, then see precision/recall per rule and the flagged transactions
(with a CSV download). The logic lives in `src/ui` and is unit tested.

## Running the tests

```
pip install pytest
pytest
```
