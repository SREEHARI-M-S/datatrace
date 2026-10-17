from typer.testing import CliRunner

from datatrace.cli.main import app

runner = CliRunner()


def test_validate_json_ok() -> None:
    result = runner.invoke(app, ["validate", "--json"])
    assert result.exit_code == 0
    assert '"ok"' in result.stdout and "true" in result.stdout
