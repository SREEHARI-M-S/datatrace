from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel

from datatrace.analysis.root_cause import first_significant_change
from datatrace.recorder.store import EventStore
from datatrace.trace.record_tracer import build_lineage

app = typer.Typer(no_args_is_help=True, help="DataTrace — data forensics")
console = Console()


@app.command()
def explain(
    record: str = typer.Option(..., "--record", help="Key=value, e.g. customer_id=183729"),
    store: Path = typer.Option(..., help="JSONL event store path"),
) -> None:
    if "=" not in record:
        raise typer.BadParameter("Use --record key=value")
    record_id = record.split("=", 1)[1]
    events = EventStore(store).load_for_record(record_id)
    if not events:
        console.print("[yellow]No events found for record.[/yellow]")
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
            ],
        )
    console.print(Panel("\n".join(lines), title=f"Record {record_id}"))


if __name__ == "__main__":
    app()
