import json
from pathlib import Path

from typer.testing import CliRunner

from datatrace.analysis.audit import audit_records
from datatrace.cli.main import app
from datatrace.recorder.store import EventStore

runner = CliRunner()


def test_audit_records_finds_root_cause() -> None:
    rows = audit_records(EventStore(Path("examples/sample_events.jsonl")))
    assert len(rows) == 1
    assert rows[0].record_id == "183729"
    assert rows[0].event_count == 3
    assert rows[0].root_cause is not None
    assert rows[0].root_cause.transformation == "identity_mapping.sql"


def test_audit_cli_json_only_changed() -> None:
    result = runner.invoke(
        app,
        ["audit", "--store", "examples/sample_events.jsonl", "--json", "--only-changed"],
    )
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert len(payload) == 1
    assert payload[0]["record_id"] == "183729"
    assert payload[0]["root_cause"]["transformation"] == "identity_mapping.sql"
