from typer.testing import CliRunner

from datatrace.cli.main import app

runner = CliRunner()


def test_records_json() -> None:
    result = runner.invoke(app, ["records", "--json"])
    assert result.exit_code == 0
    assert "183729" in result.stdout
