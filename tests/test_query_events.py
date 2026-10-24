import json
from pathlib import Path

from typer.testing import CliRunner

from datatrace.cli.main import app
from datatrace.recorder.store import EventStore

runner = CliRunner()


def test_query_events_filters_record_and_operation() -> None:
    store = EventStore(Path("examples/sample_events.jsonl"))
    hits = store.query_events(dataset="identity_mapping", operation="UPDATE", record_id="183729")
    assert len(hits) == 1
    assert hits[0].transformation == "identity_mapping.sql"


def test_search_scoped_to_record_id() -> None:
    result = runner.invoke(
        app,
        ["search", "billing", "--record-id", "183729", "--store", "examples/sample_events.jsonl"],
    )
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert len(payload) == 1
    assert payload[0]["dataset"] == "billing_export"
