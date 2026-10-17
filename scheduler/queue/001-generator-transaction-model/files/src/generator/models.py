from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class Transaction:
    """One card transaction on synthetic data.

    ``fraud_pattern`` is the ground-truth label used only for evaluation. It is
    ``None`` for legitimate transactions and the pattern name (for example
    ``"velocity"``) for injected fraud.
    """

    txn_id: str
    account_id: str
    timestamp: datetime
    amount: float
    country: str
    home_country: str
    fraud_pattern: Optional[str] = None

    @property
    def is_fraud(self) -> bool:
        return self.fraud_pattern is not None
