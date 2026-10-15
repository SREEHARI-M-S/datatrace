from typer.testing import CliRunner

from datatrace.cli.main import app

runner = CliRunner()


def test_explain_json() -> None:
    result = runner.invoke(app, ["explain", "--record", "customer_id=183729", "--json"])
    assert result.exit_code == 0
    assert "root_cause" in result.stdout
