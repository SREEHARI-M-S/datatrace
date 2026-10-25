import json
from pathlib import Path

from typer.testing import CliRunner

from datatrace.cli.main import app

runner = CliRunner()


def test_transformations_lists_sql_files() -> None:
    result = runner.invoke(
        app,
        ["transformations", "--store", "examples/sample_events.jsonl", "--json"],
    )
    assert result.exit_code == 0
    names = json.loads(result.stdout)
    assert "identity_mapping.sql" in names


def test_search_writes_output_file(tmp_path: Path) -> None:
    out = tmp_path / "hits.json"
    result = runner.invoke(
        app,
        ["search", "billing", "--store", "examples/sample_events.jsonl", "--text", "-o", str(out)],
    )
    assert result.exit_code == 0
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload[0]["dataset"] == "billing_export"
