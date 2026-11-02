import json
from pathlib import Path

from typer.testing import CliRunner

from datatrace.cli.main import app
from datatrace.models.events import TransformationEvent

runner = CliRunner()


def test_records_writes_output_file(tmp_path: Path) -> None:
    out = tmp_path / "ids.json"
    result = runner.invoke(
        app,
        ["records", "--store", "examples/sample_events.jsonl", "-o", str(out)],
    )
    assert result.exit_code == 0
    assert json.loads(out.read_text(encoding="utf-8")) == ["183729"]


def test_ingest_file_json(tmp_path: Path) -> None:
    store = tmp_path / "events.jsonl"
    event_file = tmp_path / "event.json"
    event = TransformationEvent(
        record_id="99",
        dataset="raw",
        timestamp="2024-01-01T00:00:00",
        operation="INSERT",
        transformation="load.sql",
    )
    event_file.write_text(event.model_dump_json(), encoding="utf-8")
    result = runner.invoke(
        app,
        ["ingest", "--store", str(store), "--file", str(event_file), "--json"],
    )
    assert result.exit_code == 0
    assert '"record_id": "99"' in result.stdout or '"record_id":"99"' in result.stdout
