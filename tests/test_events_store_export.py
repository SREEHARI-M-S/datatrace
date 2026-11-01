import json
from pathlib import Path

from typer.testing import CliRunner

from datatrace.cli.main import app

runner = CliRunner()


def test_events_writes_output_file(tmp_path: Path) -> None:
    out = tmp_path / "events.json"
    result = runner.invoke(
        app,
        [
            "events",
            "--dataset",
            "billing_export",
            "--store",
            "examples/sample_events.jsonl",
            "--text",
            "-o",
            str(out),
        ],
    )
    assert result.exit_code == 0
    assert len(json.loads(out.read_text(encoding="utf-8"))) == 1


def test_diff_stores_writes_output(tmp_path: Path) -> None:
    store = Path("examples/sample_events.jsonl")
    out = tmp_path / "diff.json"
    result = runner.invoke(app, ["diff-stores", str(store), str(store), "-o", str(out)])
    assert result.exit_code == 0
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["in_both"]
