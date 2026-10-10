from pathlib import Path

from typer.testing import CliRunner

from datatrace.cli.main import app
from datatrace.recorder.validate import validate_event_store

runner = CliRunner()


def test_validate_sample_store() -> None:
    issues = validate_event_store(Path("examples/sample_events.jsonl"))
    assert issues == []


def test_validate_cli_ok() -> None:
    result = runner.invoke(app, ["validate"])
    assert result.exit_code == 0
    assert "OK" in result.stdout
