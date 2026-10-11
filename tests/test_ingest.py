import json
from pathlib import Path

from typer.testing import CliRunner

from datatrace.cli.main import app
from datatrace.recorder.store import EventStore

runner = CliRunner()


def test_ingest_appends_event(tmp_path: Path) -> None:
    event = {
        "record_id": "99",
        "dataset": "test_ds",
        "timestamp": "2026-01-01T00:00:00Z",
        "operation": "INSERT",
        "before": {},
        "after": {"x": 1},
        "transformation": "t.sql",
    }
    event_file = tmp_path / "event.json"
    event_file.write_text(json.dumps(event), encoding="utf-8")
    store = tmp_path / "out.jsonl"
    result = runner.invoke(app, ["ingest", "--store", str(store), "--file", str(event_file)])
    assert result.exit_code == 0
    assert EventStore(store).stats()["events"] == 1
