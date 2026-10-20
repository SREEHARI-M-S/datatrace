from pathlib import Path

from typer.testing import CliRunner

from datatrace.cli.main import app
from datatrace.report.timeline_markdown import timeline_report_markdown
from datatrace.recorder.store import EventStore

runner = CliRunner()


def test_timeline_markdown_contains_table_header() -> None:
    events = EventStore(Path("examples/sample_events.jsonl")).load_for_record("183729")
    md = timeline_report_markdown("183729", events)
    assert "| Dataset |" in md
    assert "183729" in md


def test_filter_writes_dataset_subset(tmp_path: Path) -> None:
    out = tmp_path / "billing.jsonl"
    result = runner.invoke(
        app,
        [
            "filter",
            "--dataset",
            "billing_export",
            "--store",
            "examples/sample_events.jsonl",
            "-o",
            str(out),
        ],
    )
    assert result.exit_code == 0
    assert out.is_file()
    assert EventStore(out).stats()["events"] >= 1
