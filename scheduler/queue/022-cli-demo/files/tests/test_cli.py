from src.cli import main


def test_cli_runs_and_reports_parity(capsys):
    main(["--accounts", "10", "--days", "60", "--seed", "1"])
    out = capsys.readouterr().out
    assert "identical: True" in out
    assert "overall" in out
