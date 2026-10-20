from pathlib import Path

from typer.testing import CliRunner

from datatrace.cli.main import app
from datatrace.recorder.chronology import validate_chronology

runner = CliRunner()


def test_sample_store_passes_chronology() -> None:
    issues = validate_chronology(Path("examples/sample_events.jsonl"))
    assert not issues


def test_export_record_writes_bundle(tmp_path: Path) -> None:
    out = tmp_path / "bundle.json"
    result = runner.invoke(
        app,
        [
            "export-record",
            "--record",
            "customer_id=183729",
            "--store",
            "examples/sample_events.jsonl",
            "-o",
            str(out),
        ],
    )
    assert result.exit_code == 0
    assert '"lineage"' in out.read_text(encoding="utf-8")
