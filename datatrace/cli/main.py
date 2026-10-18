from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel

from datatrace.analysis.root_cause import first_significant_change
from datatrace.recorder.store import EventStore
from datatrace.recorder.validate import validate_event_store
from datatrace.cli.ingest import register_ingest_command
from datatrace.cli.record_diff_cmd import register_record_diff_command
from datatrace.cli.store_diff_cmd import register_store_diff_command
from datatrace.cli.timeline import register_timeline_command
from datatrace.report.markdown import explain_report_markdown
from datatrace.trace.changed_fields import diff_fields
from datatrace.trace.column_trace import trace_column
from datatrace.trace.record_tracer import build_lineage

app = typer.Typer(no_args_is_help=True, help="DataTrace — data forensics")
console = Console()

register_ingest_command(app)
register_store_diff_command(app)
register_record_diff_command(app)
register_timeline_command(app)


@app.command()
def explain(
    record: str = typer.Option(..., "--record", help="Key=value, e.g. customer_id=183729"),
    store: Path = typer.Option(
        Path("examples/sample_events.jsonl"),
        help="JSONL event store path",
    ),
    output: Path | None = typer.Option(
        None,
        "-o",
        "--output",
        help="Write markdown report to this file",
    ),
    json_out: bool = typer.Option(False, "--json", help="Print structured JSON (no panel)"),
) -> None:
    """Trace a record through recorded transformation events."""
    if "=" not in record:
        raise typer.BadParameter("Use --record key=value")
    record_id = record.split("=", 1)[1]
    events = EventStore(store).load_for_record(record_id)
    if not events:
        console.print(f"[yellow]No events found for record {record_id} in {store}[/yellow]")
        raise typer.Exit(code=1)

    lineage = build_lineage(events)
    lines = ["LINEAGE", ""]
    for dataset, _state in lineage:
        lines.append(dataset)
        lines.append("    |")
        lines.append("    v")
    if lines[-1] == "    v":
        lines = lines[:-2]

    finding = first_significant_change(events)
    if finding:
        lines.extend(
            [
                "",
                "ROOT CAUSE",
                finding.summary,
                f"Transformation: {finding.transformation}",
                f"Operation: {finding.evidence.get('operation', 'unknown')}",
            ],
        )
        before = finding.evidence.get("before")
        after = finding.evidence.get("after")
        if before or after:
            lines.append(f"Before: {before}")
            lines.append(f"After: {after}")
        for field, old, new in diff_fields(
            finding.evidence.get("before", {}) if isinstance(finding.evidence.get("before"), dict) else {},
            finding.evidence.get("after", {}) if isinstance(finding.evidence.get("after"), dict) else {},
        ):
            lines.append(f"  {field}: {old!r} → {new!r}")

    if json_out:
        payload: dict[str, object] = {
            "record_id": record_id,
            "lineage": [{"dataset": d, "state": s} for d, s in lineage],
        }
        if finding:
            payload["root_cause"] = {
                "summary": finding.summary,
                "transformation": finding.transformation,
                "evidence": finding.evidence,
            }
        console.print(json.dumps(payload, indent=2, default=str))
        raise typer.Exit(code=0)

    panel_text = "\n".join(lines)
    if output:
        md = explain_report_markdown(
            record_id,
            [dataset for dataset, _ in lineage],
            finding,
        )
        output.write_text(md, encoding="utf-8")
        console.print(f"[green]Wrote[/green] {output}")
    console.print(Panel(panel_text, title=f"Record {record_id}"))


@app.command()
def events(
    dataset: str = typer.Option(..., "--dataset", help="Dataset name"),
    store: Path = typer.Option(Path("examples/sample_events.jsonl"), help="JSONL store"),
    json_out: bool = typer.Option(True, "--json/--text", help="JSON output (default)"),
) -> None:
    """List transformation events for a dataset."""
    items = EventStore(store).events_for_dataset(dataset)
    if not items:
        console.print(f"[yellow]No events for dataset {dataset}[/yellow]")
        raise typer.Exit(code=1)
    if json_out:
        console.print(json.dumps([e.model_dump(mode="json") for e in items], indent=2, default=str))
    else:
        for e in items:
            console.print(f"{e.timestamp.isoformat()} {e.record_id} {e.operation}")


@app.command()
def column(
    record: str = typer.Option(..., "--record", help="Key=value"),
    name: str = typer.Option(..., "--column", help="Column name to trace"),
    store: Path = typer.Option(Path("examples/sample_events.jsonl"), help="JSONL store"),
    json_out: bool = typer.Option(True, "--json/--text", help="JSON output (default)"),
) -> None:
    """Trace how one column value changes across events for a record."""
    if "=" not in record:
        raise typer.BadParameter("Use --record key=value")
    record_id = record.split("=", 1)[1]
    events = EventStore(store).load_for_record(record_id)
    trail = trace_column(events, name)
    if not trail:
        console.print("[yellow]No column history found.[/yellow]")
        raise typer.Exit(code=1)
    if json_out:
        console.print(json.dumps(trail, indent=2))
    else:
        for step in trail:
            console.print(f"{step['dataset']}: {step['value']!r}")


@app.command()
def validate(
    store: Path = typer.Option(
        Path("examples/sample_events.jsonl"),
        help="JSONL event store path",
    ),
    json_out: bool = typer.Option(False, "--json", help="Print validation result as JSON"),
) -> None:
    """Validate each line in a JSONL event store."""
    issues = validate_event_store(store)
    if json_out:
        console.print(
            json.dumps(
                {
                    "ok": not issues,
                    "issues": [{"line": i.line, "message": i.message} for i in issues],
                },
                indent=2,
            ),
        )
        raise typer.Exit(code=0 if not issues else 1)
    if not issues:
        console.print(f"[green]OK[/green] {store}")
        raise typer.Exit(code=0)
    for issue in issues:
        console.print(f"[red]Line {issue.line}:[/red] {issue.message}")
    raise typer.Exit(code=1)


@app.command()
def records(
    store: Path = typer.Option(
        Path("examples/sample_events.jsonl"),
        help="JSONL event store path",
    ),
    json_out: bool = typer.Option(False, "--json", help="Print record IDs as JSON array"),
) -> None:
    """List record IDs present in the event store."""
    ids = EventStore(store).list_record_ids()
    if not ids:
        console.print("[yellow]No records found.[/yellow]")
        raise typer.Exit(code=1)
    if json_out:
        console.print(json.dumps(ids, indent=2))
        return
    for record_id in ids:
        console.print(record_id)


@app.command()
def datasets(
    store: Path = typer.Option(
        Path("examples/sample_events.jsonl"),
        help="JSONL event store path",
    ),
    json_out: bool = typer.Option(False, "--json", help="Print datasets as JSON array"),
) -> None:
    """List datasets referenced in the event store."""
    names = sorted({e.dataset for e in EventStore(store).iter_events()})
    if not names:
        console.print("[yellow]No datasets found.[/yellow]")
        raise typer.Exit(code=1)
    if json_out:
        console.print(json.dumps(names, indent=2))
        return
    for name in names:
        console.print(name)


@app.command()
def stats(
    store: Path = typer.Option(
        Path("examples/sample_events.jsonl"),
        help="JSONL event store path",
    ),
    json_out: bool = typer.Option(False, "--json", help="Print machine-readable summary"),
) -> None:
    """Summarize events in a JSONL store."""
    summary = EventStore(store).stats()
    if json_out:
        console.print(json.dumps(summary, indent=2))
        return
    console.print(
        f"Events: {summary['events']}  |  Records: {summary['records']}  |  "
        f"Datasets: {summary['datasets']}",
    )


@app.command()
def version() -> None:
    from datatrace import __version__

    console.print(f"datatrace {__version__}")


if __name__ == "__main__":
    app()
