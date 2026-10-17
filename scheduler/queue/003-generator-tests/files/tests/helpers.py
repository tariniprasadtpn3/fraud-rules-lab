from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

from src.generator.models import Transaction

BASE = datetime(2026, 3, 1, 12, 0, 0)


def make_txn(
    txn_id: str = "T1",
    account_id: str = "A1",
    days: int = 0,
    minutes: int = 0,
    amount: float = 50.0,
    country: str = "IN",
    home_country: str = "IN",
    fraud_pattern: Optional[str] = None,
) -> Transaction:
    """Build a transaction at BASE + (days, minutes) for compact test setup."""
    return Transaction(
        txn_id=txn_id,
        account_id=account_id,
        timestamp=BASE + timedelta(days=days, minutes=minutes),
        amount=amount,
        country=country,
        home_country=home_country,
        fraud_pattern=fraud_pattern,
    )
