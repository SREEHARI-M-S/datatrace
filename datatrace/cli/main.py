from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel

from datatrace.analysis.root_cause import first_significant_change
from datatrace.recorder.store import EventStore
from datatrace.recorder.validate import validate_event_store
from datatrace.trace.changed_fields import diff_fields
from datatrace.trace.record_tracer import build_lineage

app = typer.Typer(no_args_is_help=True, help="DataTrace — data forensics")
console = Console()


@app.command()
def explain(
    record: str = typer.Option(..., "--record", help="Key=value, e.g. customer_id=183729"),
    store: Path = typer.Option(
        Path("examples/sample_events.jsonl"),
        help="JSONL event store path",
    ),
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

    console.print(Panel("\n".join(lines), title=f"Record {record_id}"))


@app.command()
def validate(
    store: Path = typer.Option(
        Path("examples/sample_events.jsonl"),
        help="JSONL event store path",
    ),
) -> None:
    """Validate each line in a JSONL event store."""
    issues = validate_event_store(store)
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
) -> None:
    """List record IDs present in the event store."""
    ids = EventStore(store).list_record_ids()
    if not ids:
        console.print("[yellow]No records found.[/yellow]")
        raise typer.Exit(code=1)
    for record_id in ids:
        console.print(record_id)


@app.command()
def stats(
    store: Path = typer.Option(
        Path("examples/sample_events.jsonl"),
        help="JSONL event store path",
    ),
) -> None:
    """Summarize events in a JSONL store."""
    summary = EventStore(store).stats()
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
