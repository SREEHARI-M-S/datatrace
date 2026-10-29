import json
from pathlib import Path

from typer.testing import CliRunner

from datatrace.cli.main import app

runner = CliRunner()


def test_validate_writes_output_file(tmp_path: Path) -> None:
    out = tmp_path / "validate.json"
    result = runner.invoke(
        app,
        ["validate", "--store", "examples/sample_events.jsonl", "-o", str(out), "--chronology"],
    )
    assert result.exit_code == 0
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["ok"] is True


def test_column_writes_output_file(tmp_path: Path) -> None:
    out = tmp_path / "trail.json"
    result = runner.invoke(
        app,
        [
            "column",
            "--record",
            "customer_id=183729",
            "--column",
            "identity_id",
            "--store",
            "examples/sample_events.jsonl",
            "--text",
            "-o",
            str(out),
        ],
    )
    assert result.exit_code == 0
    trail = json.loads(out.read_text(encoding="utf-8"))
    assert len(trail) >= 1
