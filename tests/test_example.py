from examples.end_to_end import run_demo


def test_demo_is_deterministic_and_has_overall_metrics():
    first, second = run_demo(seed=7), run_demo(seed=7)
    assert "overall" in first
    assert {k: (v.tp, v.fp, v.fn) for k, v in first.items()} == {
        k: (v.tp, v.fp, v.fn) for k, v in second.items()
    }
