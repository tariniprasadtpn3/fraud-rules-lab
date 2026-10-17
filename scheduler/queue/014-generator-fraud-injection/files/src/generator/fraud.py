from __future__ import annotations

import itertools
import random
from datetime import timedelta
from typing import Dict, List

from .models import Transaction
from .synthetic import COUNTRIES, START

PATTERNS = ("velocity", "amount_spike", "geo_mismatch", "dormant_reactivation")

BURST_SIZE = 8


def inject_fraud(
    transactions: List[Transaction], seed: int = 7, per_pattern: int = 5
) -> List[Transaction]:
    """Return ``transactions`` plus labelled fraud for each known pattern.

    - velocity: a burst of ``BURST_SIZE`` small purchases a minute apart
    - amount_spike: one purchase 10-20x the account's average
    - geo_mismatch: one sizeable purchase from a new foreign country
    - dormant_reactivation: a large purchase on a long-silent account
      (the account is created here, with a few early legitimate transactions)

    Every injected fraud transaction carries its pattern name in
    ``fraud_pattern``; the helper transactions for dormant accounts are
    legitimate and unlabelled. The input list is not modified.
    """
    rng = random.Random(seed)
    out = list(transactions)

    by_account: Dict[str, List[Transaction]] = {}
    for t in transactions:
        by_account.setdefault(t.account_id, []).append(t)
    accounts = sorted(by_account)
    per_pattern = min(per_pattern, len(accounts))

    fraud_ids = (f"F{n:06d}" for n in itertools.count())
    helper_ids = (f"D{n:06d}" for n in itertools.count())

    for acct in rng.sample(accounts, per_pattern):
        anchor = rng.choice(by_account[acct])
        for i in range(BURST_SIZE):
            out.append(
                Transaction(
                    txn_id=next(fraud_ids),
                    account_id=acct,
                    timestamp=anchor.timestamp + timedelta(minutes=1 + i),
                    amount=round(rng.uniform(5, 25), 2),
                    country=anchor.home_country,
                    home_country=anchor.home_country,
                    fraud_pattern="velocity",
                )
            )

    for acct in rng.sample(accounts, per_pattern):
        history = by_account[acct]
        last = max(history, key=lambda t: t.timestamp)
        mean = sum(t.amount for t in history) / len(history)
        out.append(
            Transaction(
                txn_id=next(fraud_ids),
                account_id=acct,
                timestamp=last.timestamp + timedelta(hours=1),
                amount=round(mean * rng.uniform(10, 20), 2),
                country=last.home_country,
                home_country=last.home_country,
                fraud_pattern="amount_spike",
            )
        )

    for acct in rng.sample(accounts, per_pattern):
        last = max(by_account[acct], key=lambda t: t.timestamp)
        foreign = rng.choice([c for c in COUNTRIES if c != last.home_country])
        out.append(
            Transaction(
                txn_id=next(fraud_ids),
                account_id=acct,
                timestamp=last.timestamp + timedelta(hours=2),
                amount=round(rng.uniform(150, 500), 2),
                country=foreign,
                home_country=last.home_country,
                fraud_pattern="geo_mismatch",
            )
        )

    for d in range(max(1, per_pattern // 2)):
        acct = f"DORM{d:03d}"
        home = rng.choice(COUNTRIES)
        for day in range(5):
            out.append(
                Transaction(
                    txn_id=next(helper_ids),
                    account_id=acct,
                    timestamp=START + timedelta(days=day, hours=10),
                    amount=round(rng.uniform(30, 80), 2),
                    country=home,
                    home_country=home,
                )
            )
        out.append(
            Transaction(
                txn_id=next(fraud_ids),
                account_id=acct,
                timestamp=START + timedelta(days=rng.randint(150, 170), hours=11),
                amount=round(rng.uniform(200, 800), 2),
                country=home,
                home_country=home,
                fraud_pattern="dormant_reactivation",
            )
        )

    out.sort(key=lambda t: (t.timestamp, t.txn_id))
    return out
