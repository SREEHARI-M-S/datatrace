from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from datatrace.recorder.store import EventStore

console = Console()


def register_timeline_command(app: typer.Typer) -> None:
    @app.command("timeline")
    def timeline(
        record: str = typer.Option(..., "--record", help="Key=value"),
        store: Path = typer.Option(Path("examples/sample_events.jsonl"), help="JSONL store"),
    ) -> None:
        """Chronological event table for one record."""
        if "=" not in record:
            raise typer.BadParameter("Use --record key=value")
        record_id = record.split("=", 1)[1]
        events = EventStore(store).load_for_record(record_id)
        if not events:
            console.print("[yellow]No events found.[/yellow]")
            raise typer.Exit(code=1)

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
