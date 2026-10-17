from datetime import timedelta

import pytest

from src.rules.base import Flag, Rule, within
from tests.helpers import BASE, make_txn


def test_within_keeps_only_recent_transactions():
    history = [make_txn("T1", minutes=-30), make_txn("T2", minutes=-5)]
    recent = within(history, BASE, timedelta(minutes=10))
    assert [t.txn_id for t in recent] == ["T2"]


def test_within_is_inclusive_at_the_cutoff():
    history = [make_txn("T1", minutes=-10)]
    assert len(within(history, BASE, timedelta(minutes=10))) == 1


def test_rule_cannot_be_instantiated_directly():
    with pytest.raises(TypeError):
        Rule()


def test_flag_equality_and_hashing():
    assert Flag("T1", "velocity") == Flag("T1", "velocity")
    assert len({Flag("T1", "velocity"), Flag("T1", "velocity")}) == 1
