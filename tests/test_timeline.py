from typer.testing import CliRunner

from datatrace.cli.main import app

runner = CliRunner()


def test_timeline_cli() -> None:
    result = runner.invoke(app, ["timeline", "--record", "customer_id=183729"])
    assert result.exit_code == 0
    assert "identity_mapping" in result.stdout
