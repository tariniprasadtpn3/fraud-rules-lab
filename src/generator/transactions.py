"""Synthetic transaction generator with a fixed seed and injected fraud patterns.

All data produced here is synthetic. Nothing comes from any real bank,
employer or client.

Each account gets a home country, a typical amount and a stream of normal
transactions. A fraction of accounts then receive exactly one injected fraud
pattern, so rules can later be scored with precision and recall against the
ground-truth labels (`is_fraud`, `fraud_pattern`).
"""

from __future__ import annotations

import csv
import random
from dataclasses import dataclass, replace
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable, List, Optional

CATEGORIES = ("grocery", "fuel", "dining", "travel", "electronics", "utilities", "fashion")
COUNTRIES = ("IN", "US", "GB", "SG", "AE")

VELOCITY = "velocity"
AMOUNT_SPIKE = "amount_spike"
GEO_MISMATCH = "geo_mismatch"
DORMANT_REACTIVATION = "dormant_reactivation"
PATTERNS = (VELOCITY, AMOUNT_SPIKE, GEO_MISMATCH, DORMANT_REACTIVATION)

DEFAULT_START = datetime(2026, 1, 1)


@dataclass(frozen=True)
class Transaction:
    """A single synthetic card transaction with ground-truth fraud labels."""

    txn_id: str
    account_id: str
    timestamp: datetime
    amount: float
    merchant_category: str
    country: str
    is_fraud: bool = False
    fraud_pattern: Optional[str] = None


def generate_transactions(
    n_accounts: int = 50,
    days: int = 30,
    fraud_account_ratio: float = 0.2,
    seed: int = 42,
    start: datetime = DEFAULT_START,
) -> List[Transaction]:
    """Return a reproducible, time-ordered list of synthetic transactions.

    The same arguments always produce the same output. `fraud_account_ratio`
    is the share of accounts that receive one injected fraud pattern, cycling
    through `PATTERNS` so every pattern appears when enough accounts are
    chosen.
    """
    if n_accounts <= 0:
        raise ValueError("n_accounts must be positive")
    if days < 6:
        raise ValueError("days must be at least 6")
    if not 0.0 <= fraud_account_ratio <= 1.0:
        raise ValueError("fraud_account_ratio must be between 0 and 1")

    rng = random.Random(seed)
    account_ids = [f"ACC{i:04d}" for i in range(1, n_accounts + 1)]
    profiles = {
        acc: {
            "home": rng.choice(COUNTRIES),
            "mean": round(rng.uniform(500.0, 5000.0), 2),
        }
        for acc in account_ids
    }

    n_fraud = round(n_accounts * fraud_account_ratio)
    fraud_accounts = rng.sample(account_ids, n_fraud)
    pattern_for = {acc: PATTERNS[i % len(PATTERNS)] for i, acc in enumerate(fraud_accounts)}

    quiet_window_days = max(1, days // 3)
    raw: List[Transaction] = []

    for acc in account_ids:
        home = profiles[acc]["home"]
        mean = profiles[acc]["mean"]
        pattern = pattern_for.get(acc)

        # Dormant accounts only trade in the first third of the period.
        active_days = quiet_window_days if pattern == DORMANT_REACTIVATION else days
        for _ in range(rng.randint(15, 40)):
            ts = start + timedelta(seconds=rng.randint(0, active_days * 86400 - 1))
            raw.append(
                Transaction(
                    txn_id="",
                    account_id=acc,
                    timestamp=ts,
                    amount=round(mean * rng.uniform(0.3, 1.7), 2),
                    merchant_category=rng.choice(CATEGORIES),
                    country=home,
                )
            )

        if pattern is not None:
            raw.extend(_inject(rng, pattern, acc, home, mean, days, start))

    raw.sort(key=lambda t: (t.timestamp, t.account_id))
    return [replace(t, txn_id=f"TXN{i:06d}") for i, t in enumerate(raw, start=1)]


def _inject(
    rng: random.Random,
    pattern: str,
    account_id: str,
    home: str,
    mean: float,
    days: int,
    start: datetime,
) -> List[Transaction]:
    """Build the fraudulent transactions for one account and one pattern."""

    def fraud(ts: datetime, amount: float, country: str, category: str) -> Transaction:
        return Transaction(
            txn_id="",
            account_id=account_id,
            timestamp=ts,
            amount=round(amount, 2),
            merchant_category=category,
            country=country,
            is_fraud=True,
            fraud_pattern=pattern,
        )

    if pattern == VELOCITY:
        # Six small purchases inside a four-minute burst.
        base = start + timedelta(seconds=rng.randint(86400, (days - 1) * 86400))
        offsets = sorted(rng.randint(0, 240) for _ in range(6))
        return [
            fraud(base + timedelta(seconds=o), mean * rng.uniform(0.05, 0.2), home, "electronics")
            for o in offsets
        ]

    if pattern == AMOUNT_SPIKE:
        # One purchase far above the account's normal range (normal max is 1.7x mean).
        ts = start + timedelta(seconds=rng.randint(86400, (days - 1) * 86400))
        return [fraud(ts, mean * rng.uniform(15.0, 30.0), home, rng.choice(CATEGORIES))]

    if pattern == GEO_MISMATCH:
        # A purchase in a country that is not the account's home country.
        foreign = rng.choice([c for c in COUNTRIES if c != home])
        ts = start + timedelta(seconds=rng.randint(86400, (days - 1) * 86400))
        return [fraud(ts, mean * rng.uniform(0.5, 1.5), foreign, "travel")]

    if pattern == DORMANT_REACTIVATION:
        # A large purchase on the last day, long after the account went quiet.
        ts = start + timedelta(days=days - 1, seconds=rng.randint(0, 86399))
        return [fraud(ts, mean * rng.uniform(10.0, 20.0), home, rng.choice(CATEGORIES))]

    raise ValueError(f"unknown pattern: {pattern}")


def write_csv(transactions: Iterable[Transaction], path: Path) -> None:
    """Write transactions to a CSV file, creating parent folders if needed."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "txn_id",
        "account_id",
        "timestamp",
        "amount",
        "merchant_category",
        "country",
        "is_fraud",
        "fraud_pattern",
    ]
    with path.open("w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(fields)
        for t in transactions:
            writer.writerow(
                [
                    t.txn_id,
                    t.account_id,
                    t.timestamp.isoformat(),
                    f"{t.amount:.2f}",
                    t.merchant_category,
                    t.country,
                    int(t.is_fraud),
                    t.fraud_pattern or "",
                ]
            )
