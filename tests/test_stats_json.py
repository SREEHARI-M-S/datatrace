from typer.testing import CliRunner

from datatrace.cli.main import app

runner = CliRunner()


def test_stats_json() -> None:
    result = runner.invoke(app, ["stats", "--json"])
    assert result.exit_code == 0
    assert '"events"' in result.stdout
