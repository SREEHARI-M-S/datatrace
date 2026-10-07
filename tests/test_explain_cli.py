from pathlib import Path

from typer.testing import CliRunner

from datatrace.cli.main import app

runner = CliRunner()


def test_explain_sample_record() -> None:
    store = Path("examples/sample_events.jsonl")
    result = runner.invoke(
        app,
        ["explain", "--record", "customer_id=183729", "--store", str(store)],
    )
    assert result.exit_code == 0
    assert "identity_mapping" in result.stdout
    assert "identity_mapping.sql" in result.stdout
