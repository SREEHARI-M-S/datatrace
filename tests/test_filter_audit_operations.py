import json
from pathlib import Path

from typer.testing import CliRunner

from datatrace.cli.main import app
from datatrace.recorder.store import EventStore

runner = CliRunner()


def test_filter_by_operation(tmp_path: Path) -> None:
    out = tmp_path / "updates.jsonl"
    result = runner.invoke(
        app,
        [
            "filter",
            "--dataset",
            "identity_mapping",
            "--operation",
            "UPDATE",
            "--store",
            "examples/sample_events.jsonl",
            "-o",
            str(out),
        ],
    )
    assert result.exit_code == 0
    lines = out.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    assert '"operation":"UPDATE"' in lines[0]


def test_filter_by_record_id(tmp_path: Path) -> None:
    out = tmp_path / "one.jsonl"
    result = runner.invoke(
        app,
        [
            "filter",
            "--dataset",
            "raw_customer",
            "--record-id",
            "183729",
            "--store",
            "examples/sample_events.jsonl",
            "-o",
            str(out),
        ],
    )
    assert result.exit_code == 0
    assert len(out.read_text(encoding="utf-8").strip().splitlines()) == 1


def test_operations_cli() -> None:
    result = runner.invoke(app, ["operations", "--store", "examples/sample_events.jsonl", "--json"])
    assert result.exit_code == 0
    assert json.loads(result.stdout) == ["INSERT", "UPDATE"]


def test_audit_writes_output_file(tmp_path: Path) -> None:
    out = tmp_path / "audit.json"
    result = runner.invoke(
        app,
        ["audit", "--store", "examples/sample_events.jsonl", "-o", str(out)],
    )
    assert result.exit_code == 0
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload[0]["record_id"] == "183729"
    assert EventStore(Path("examples/sample_events.jsonl")).list_operations()
