import pytest

from src.ui import available_rules, flagged_frame, metrics_frame, run_pipeline


def test_available_rules_lists_all_ten():
    assert len(available_rules()) == 10


def test_run_pipeline_is_deterministic_and_filters_rules():
    a = run_pipeline(seed=3, rule_names=["velocity", "geo_mismatch"])
    b = run_pipeline(seed=3, rule_names=["velocity", "geo_mismatch"])
    assert a.flagged == b.flagged
    assert {r for f in a.flagged for r in f.rules} <= {"velocity", "geo_mismatch"}


def test_run_pipeline_rejects_no_rules():
    with pytest.raises(ValueError):
        run_pipeline(rule_names=[])


def test_frames_have_expected_shape():
    result = run_pipeline(seed=1)
    flagged = flagged_frame(result.flagged)
    assert len(flagged) == len(result.flagged)
    assert {"txn_id", "rules", "is_fraud"} <= set(flagged.columns)
    metrics = metrics_frame(result.metrics)
    assert metrics.index[0] == "overall"
    assert metrics["precision"].between(0, 1).all()


def test_empty_flagged_frame_keeps_columns():
    assert list(flagged_frame([]).columns)[:2] == ["txn_id", "account_id"]


def test_streamlit_app_runs_without_exception():
    pytest.importorskip("streamlit")
    from streamlit.testing.v1 import AppTest

    at = AppTest.from_file("../streamlit_app.py", default_timeout=60).run()
    assert not at.exception
    assert at.title[0].value == "Fraud rules lab"
