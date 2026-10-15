from typer.testing import CliRunner

from datatrace.cli.main import app

runner = CliRunner()


def test_column_trace_identity_id() -> None:
    result = runner.invoke(
        app,
        ["column", "--record", "customer_id=183729", "--column", "identity_id", "--json"],
    )
    assert result.exit_code == 0
    assert "abc123" in result.stdout
