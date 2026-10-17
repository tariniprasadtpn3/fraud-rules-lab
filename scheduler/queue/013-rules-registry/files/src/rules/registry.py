from __future__ import annotations

from typing import List

from .amount_spike import AmountSpikeRule
from .base import Rule
from .dormant import DormantReactivationRule
from .geo_mismatch import GeoMismatchRule
from .velocity import VelocityRule


def default_rules() -> List[Rule]:
    """Fresh instances of every rule with their default thresholds."""
    return [
        VelocityRule(),
        AmountSpikeRule(),
        GeoMismatchRule(),
        DormantReactivationRule(),
    ]
