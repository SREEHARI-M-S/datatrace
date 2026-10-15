from typer.testing import CliRunner

from datatrace.cli.main import app

runner = CliRunner()


def test_events_for_dataset() -> None:
    result = runner.invoke(app, ["events", "--dataset", "identity_mapping", "--json"])
    assert result.exit_code == 0
    assert "183729" in result.stdout
