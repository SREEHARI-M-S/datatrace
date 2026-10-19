from pathlib import Path

from typer.testing import CliRunner

from datatrace.cli.main import app
from datatrace.recorder.store import EventStore

runner = CliRunner()


def test_events_per_dataset_counts() -> None:
    store = EventStore(Path("examples/sample_events.jsonl"))
    counts = store.events_per_dataset()
    assert counts
    assert sum(counts.values()) == store.stats()["events"]


def test_search_cli_finds_events() -> None:
    result = runner.invoke(app, ["search", "billing", "--store", "examples/sample_events.jsonl"])
    assert result.exit_code == 0
    assert "dataset" in result.stdout.lower() or "record_id" in result.stdout
