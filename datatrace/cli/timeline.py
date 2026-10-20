from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from datatrace.recorder.store import EventStore
from datatrace.report.timeline_markdown import timeline_report_markdown

console = Console()


def register_timeline_command(app: typer.Typer) -> None:
    @app.command("timeline")
    def timeline(
        record: str = typer.Option(..., "--record", help="Key=value"),
        store: Path = typer.Option(Path("examples/sample_events.jsonl"), help="JSONL store"),
        json_out: bool = typer.Option(False, "--json", help="Print timeline as JSON"),
        output: Path | None = typer.Option(
            None,
            "-o",
            "--output",
            help="Write markdown timeline to this file",
        ),
    ) -> None:
        """Chronological event table for one record."""
        if "=" not in record:
            raise typer.BadParameter("Use --record key=value")
        record_id = record.split("=", 1)[1]
        events = EventStore(store).load_for_record(record_id)
        if not events:
            console.print("[yellow]No events found.[/yellow]")
            raise typer.Exit(code=1)

        if output is not None:
            output.write_text(timeline_report_markdown(record_id, events), encoding="utf-8")
            console.print(f"[green]Wrote[/green] {output}")

        if json_out:
            console.print(
                json.dumps(
                    [e.model_dump(mode="json") for e in events],
                    indent=2,
                    default=str,
                ),
            )
            return

        if output is not None:
            return

        table = Table(title=f"Timeline {record_id}")
        table.add_column("Time")
        table.add_column("Dataset")
        table.add_column("Op")
        table.add_column("Transformation")
        for event in events:
            table.add_row(
                event.timestamp.isoformat(),
                event.dataset,
                event.operation,
                event.transformation,
            )
        console.print(table)
