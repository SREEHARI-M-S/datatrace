import json
from pathlib import Path

from typer.testing import CliRunner

from datatrace.cli.main import app

runner = CliRunner()


def test_ingest_merge_json_summary(tmp_path: Path) -> None:
    source = Path("examples/sample_events.jsonl")
    target = tmp_path / "merged.jsonl"
    result = runner.invoke(
        app,
        ["ingest", "--store", str(target), "--merge", str(source), "--json"],
    )
    assert result.exit_code == 0
    assert '"merged": 3' in result.stdout
    assert '"skipped_duplicates": 0' in result.stdout
