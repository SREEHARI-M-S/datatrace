from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel

from datatrace.analysis.root_cause import first_significant_change
from datatrace.recorder.store import EventStore
from datatrace.recorder.chronology import validate_chronology
from datatrace.recorder.validate import validate_event_store
from datatrace.cli.ingest import register_ingest_command
from datatrace.cli.record_diff_cmd import register_record_diff_command
from datatrace.cli.store_diff_cmd import register_store_diff_command
from datatrace.cli.timeline import register_timeline_command
from datatrace.cli.search_cmd import register_search_command
from datatrace.cli.filter_cmd import register_filter_command
from datatrace.cli.export_record_cmd import register_export_record_command
from datatrace.cli.audit_cmd import register_audit_command
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
register_search_command(app)
register_filter_command(app)
register_export_record_command(app)
register_audit_command(app)


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
        text = json.dumps(payload, indent=2, default=str)
        if output is not None:
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(text, encoding="utf-8")
            console.print(f"[green]Wrote[/green] {output}")
        else:
            console.print(text)
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
    operation: str | None = typer.Option(None, "--operation", help="Filter by operation"),
    record_id: str | None = typer.Option(None, "--record-id", help="Filter by record id"),
    store: Path = typer.Option(Path("examples/sample_events.jsonl"), help="JSONL store"),
    json_out: bool = typer.Option(True, "--json/--text", help="JSON output (default)"),
    output: Path | None = typer.Option(None, "-o", "--output", help="Write events JSON to file"),
) -> None:
    """List transformation events for a dataset."""
    items = EventStore(store).query_events(
        dataset=dataset,
        operation=operation,
        record_id=record_id,
    )
    if not items:
        console.print(f"[yellow]No events for dataset {dataset}[/yellow]")
        raise typer.Exit(code=1)
    payload = [e.model_dump(mode="json") for e in items]
    text = json.dumps(payload, indent=2, default=str)
    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text, encoding="utf-8")
        console.print(f"[green]Wrote[/green] {output}")
    if json_out:
        console.print(text)
        return
    if output is not None:
        return
    for e in items:
        console.print(f"{e.timestamp.isoformat()} {e.record_id} {e.operation}")


@app.command()
def column(
    record: str = typer.Option(..., "--record", help="Key=value"),
    name: str = typer.Option(..., "--column", help="Column name to trace"),
    store: Path = typer.Option(Path("examples/sample_events.jsonl"), help="JSONL store"),
    json_out: bool = typer.Option(True, "--json/--text", help="JSON output (default)"),
    output: Path | None = typer.Option(None, "-o", "--output", help="Write column trail JSON to file"),
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
    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(trail, indent=2), encoding="utf-8")
        console.print(f"[green]Wrote[/green] {output}")
    if json_out:
        console.print(json.dumps(trail, indent=2))
        return
    if output is not None:
        return
    for step in trail:
        console.print(f"{step['dataset']}: {step['value']!r}")


@app.command()
def validate(
    store: Path = typer.Option(
        Path("examples/sample_events.jsonl"),
        help="JSONL event store path",
    ),
    json_out: bool = typer.Option(False, "--json", help="Print validation result as JSON"),
    chronology: bool = typer.Option(
        False,
        "--chronology",
        help="Also require non-decreasing timestamps per record",
    ),
    output: Path | None = typer.Option(None, "-o", "--output", help="Write validation JSON to file"),
) -> None:
    """Validate each line in a JSONL event store."""
    issues = validate_event_store(store)
    chrono_issues = validate_chronology(store) if chronology else []
    ok = not issues and not chrono_issues
    document = {
        "ok": ok,
        "store": str(store),
        "issues": [{"line": i.line, "message": i.message} for i in issues],
        "chronology": [{"record_id": c.record_id, "message": c.message} for c in chrono_issues],
    }
    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(document, indent=2), encoding="utf-8")
        console.print(f"[green]Wrote[/green] {output}")
    if json_out:
        console.print(json.dumps(document, indent=2))
        raise typer.Exit(code=0 if ok else 1)
    if output is not None:
        raise typer.Exit(code=0 if ok else 1)
    if ok:
        console.print(f"[green]OK[/green] {store}")
        raise typer.Exit(code=0)
    for issue in issues:
        console.print(f"[red]Line {issue.line}:[/red] {issue.message}")
    for issue in chrono_issues:
        console.print(f"[red]Record {issue.record_id}:[/red] {issue.message}")
    raise typer.Exit(code=1)


@app.command()
def records(
    store: Path = typer.Option(
        Path("examples/sample_events.jsonl"),
        help="JSONL event store path",
    ),
    dataset: str | None = typer.Option(
        None,
        "--dataset",
        help="Only list records that appear in this dataset",
    ),
    json_out: bool = typer.Option(False, "--json", help="Print record IDs as JSON array"),
) -> None:
    """List record IDs present in the event store."""
    ids = EventStore(store).list_record_ids(dataset=dataset)
    if not ids:
        console.print("[yellow]No records found.[/yellow]")
        raise typer.Exit(code=1)
    if json_out:
        console.print(json.dumps(ids, indent=2))
        return
    for record_id in ids:
        console.print(record_id)


@app.command()
def operations(
    store: Path = typer.Option(
        Path("examples/sample_events.jsonl"),
        help="JSONL event store path",
    ),
    json_out: bool = typer.Option(False, "--json", help="Print operations as JSON array"),
) -> None:
    """List transformation operations present in the event store."""
    names = EventStore(store).list_operations()
    if not names:
        console.print("[yellow]No operations found.[/yellow]")
        raise typer.Exit(code=1)
    if json_out:
        console.print(json.dumps(names, indent=2))
        return
    for name in names:
        console.print(name)


@app.command()
def transformations(
    store: Path = typer.Option(
        Path("examples/sample_events.jsonl"),
        help="JSONL event store path",
    ),
    json_out: bool = typer.Option(False, "--json", help="Print transformations as JSON array"),
) -> None:
    """List SQL transformation names referenced in the event store."""
    names = EventStore(store).list_transformations()
    if not names:
        console.print("[yellow]No transformations found.[/yellow]")
        raise typer.Exit(code=1)
    if json_out:
        console.print(json.dumps(names, indent=2))
        return
    for name in names:
        console.print(name)


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
    by_dataset: bool = typer.Option(False, "--by-dataset", help="Include per-dataset event counts"),
    by_operation: bool = typer.Option(False, "--by-operation", help="Include per-operation event counts"),
    by_transformation: bool = typer.Option(
        False,
        "--by-transformation",
        help="Include per-transformation SQL file event counts",
    ),
) -> None:
    """Summarize events in a JSONL store."""
    event_store = EventStore(store)
    summary = event_store.stats()
    if by_dataset:
        summary = {**summary, "events_per_dataset": event_store.events_per_dataset()}
    if by_operation:
        summary = {**summary, "events_per_operation": event_store.events_per_operation()}
    if by_transformation:
        summary = {**summary, "events_per_transformation": event_store.events_per_transformation()}
    if json_out:
        console.print(json.dumps(summary, indent=2))
        return
    console.print(
        f"Events: {summary['events']}  |  Records: {summary['records']}  |  "
        f"Datasets: {summary['datasets']}",
    )
    if by_dataset and "events_per_dataset" in summary:
        for name, count in summary["events_per_dataset"].items():
            console.print(f"  {name}: {count}")
    if by_operation and "events_per_operation" in summary:
        for name, count in summary["events_per_operation"].items():
            console.print(f"  {name}: {count}")
    if by_transformation and "events_per_transformation" in summary:
        for name, count in summary["events_per_transformation"].items():
            console.print(f"  {name}: {count}")


@app.command()
def version() -> None:
    from datatrace import __version__

    console.print(f"datatrace {__version__}")


if __name__ == "__main__":
    app()
