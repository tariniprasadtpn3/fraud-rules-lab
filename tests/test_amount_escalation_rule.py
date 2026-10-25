from datetime import datetime, timedelta

import pytest

from src.generator import Transaction
from src.rules import AmountEscalationRule, Rule

T0 = datetime(2026, 3, 1, 12, 0)


def _txn(i: int, amount: float) -> Transaction:
    return Transaction(f"T{i}", "ACC0001", T0 + timedelta(hours=i), amount, "grocery", "IN")


def _hist(amounts):
    return [_txn(i, a) for i, a in enumerate(amounts)]


def test_implements_interface():
    assert isinstance(AmountEscalationRule(), Rule)
    assert AmountEscalationRule().name == "amount_escalation"


def test_flags_escalating_run():
    assert AmountEscalationRule().evaluate(_txn(9, 100.0), _hist([40, 60])) is True


def test_only_recent_history_matters():
    assert AmountEscalationRule().evaluate(_txn(9, 100.0), _hist([500, 10, 40, 60])) is True


def test_small_growth_not_flagged():
    assert AmountEscalationRule().evaluate(_txn(9, 62.0), _hist([40, 55])) is False


def test_non_monotonic_not_flagged():
    assert AmountEscalationRule().evaluate(_txn(9, 100.0), _hist([60, 40])) is False


def test_short_history_not_flagged():
    assert AmountEscalationRule().evaluate(_txn(9, 100.0), _hist([40])) is False


def test_custom_steps():
    rule = AmountEscalationRule(steps=2, min_growth=2.0)
    assert rule.evaluate(_txn(9, 100.0), _hist([40])) is True
    assert rule.evaluate(_txn(9, 70.0), _hist([40])) is False


def test_invalid_parameters():
    with pytest.raises(ValueError):
        AmountEscalationRule(steps=1)
    with pytest.raises(ValueError):
        AmountEscalationRule(min_growth=1.0)
