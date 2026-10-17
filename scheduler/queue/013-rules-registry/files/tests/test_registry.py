from src.rules.registry import default_rules


def test_default_rules_have_unique_names():
    names = [r.name for r in default_rules()]
    assert len(names) == len(set(names)) == 4


def test_default_rules_returns_fresh_instances():
    assert default_rules()[0] is not default_rules()[0]
