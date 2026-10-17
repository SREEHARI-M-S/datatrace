import json
from pathlib import Path

from typer.testing import CliRunner

from datatrace.cli.main import app
from datatrace.diff.store_diff import diff_record_ids
from datatrace.recorder.store import EventStore

runner = CliRunner()


def test_diff_record_ids(tmp_path: Path) -> None:
    a = tmp_path / "a.jsonl"
    b = tmp_path / "b.jsonl"
    line = {
        "record_id": "1",
        "dataset": "d",
        "timestamp": "2026-01-01T00:00:00Z",
        "operation": "INSERT",
        "before": {},
        "after": {},
        "transformation": "t.sql",
    }
    a.write_text(json.dumps(line) + "\n", encoding="utf-8")
    b.write_text("", encoding="utf-8")
    summary = diff_record_ids(EventStore(a), EventStore(b))
    assert summary.only_in_a == ["1"]


def test_diff_stores_cli(tmp_path: Path) -> None:
    a = tmp_path / "a.jsonl"
    b = tmp_path / "b.jsonl"
    a.write_text(Path("examples/sample_events.jsonl").read_text(encoding="utf-8"), encoding="utf-8")
    b.write_text("", encoding="utf-8")
    result = runner.invoke(app, ["diff-stores", str(a), str(b), "--json"])
    assert result.exit_code == 0
    assert "only_in_a" in result.stdout
    assert "dataset_counts_a" in result.stdout


def test_dataset_counts_in_summary(tmp_path: Path) -> None:
    a = tmp_path / "a.jsonl"
    a.write_text(Path("examples/sample_events.jsonl").read_text(encoding="utf-8"), encoding="utf-8")
    from datatrace.diff.store_diff import diff_record_ids
    from datatrace.recorder.store import EventStore

    summary = diff_record_ids(EventStore(a), EventStore(a))
    assert summary.dataset_counts_a.get("identity_mapping") == 1
