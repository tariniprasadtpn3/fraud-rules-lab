from __future__ import annotations

import random
from datetime import datetime, timedelta
from typing import List

from .models import Transaction

COUNTRIES = ["IN", "US", "GB", "DE", "SG", "AE"]
START = datetime(2026, 1, 1)


def generate_transactions(
    n_accounts: int = 50, days: int = 120, seed: int = 42
) -> List[Transaction]:
    """Generate clean (unlabelled) transactions, reproducible for a given seed.

    Every account transacts only in its home country, 0-2 times a day, with
    amounts drawn from a log-normal distribution around an account-specific
    typical spend. Fraud patterns are injected separately (see ``fraud.py``).
    """
    rng = random.Random(seed)
    txns: List[Transaction] = []
    counter = 0
    for a in range(n_accounts):
        account_id = f"ACC{a:05d}"
        home = rng.choice(COUNTRIES)
        typical = rng.uniform(20, 120)
        for day in range(days):
            for _ in range(rng.choice([0, 0, 1, 1, 2])):
                seconds = rng.randrange(8 * 3600, 22 * 3600)
                amount = round(rng.lognormvariate(0, 0.5) * typical, 2)
                txns.append(
                    Transaction(
                        txn_id=f"T{counter:07d}",
                        account_id=account_id,
                        timestamp=START + timedelta(days=day, seconds=seconds),
                        amount=amount,
                        country=home,
                        home_country=home,
                    )
                )
                counter += 1
    txns.sort(key=lambda t: (t.timestamp, t.txn_id))
    return txns
