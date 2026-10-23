import json
from pathlib import Path

from typer.testing import CliRunner

from datatrace.cli.main import app
from datatrace.recorder.store import EventStore

runner = CliRunner()


def test_list_record_ids_filtered_by_dataset() -> None:
    store = EventStore(Path("examples/sample_events.jsonl"))
    assert store.list_record_ids(dataset="billing_export") == ["183729"]
    assert store.list_record_ids(dataset="missing") == []


def test_stats_by_operation_cli() -> None:
    result = runner.invoke(
        app,
        ["stats", "--store", "examples/sample_events.jsonl", "--json", "--by-operation"],
    )
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["events_per_operation"] == {"INSERT": 2, "UPDATE": 1}
