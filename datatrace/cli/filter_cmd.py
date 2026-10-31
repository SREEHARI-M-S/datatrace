from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from datatrace.recorder.store import EventStore

console = Console()


def register_filter_command(app: typer.Typer) -> None:
    @app.command("filter")
    def filter_events(
        dataset: str = typer.Option(..., "--dataset", help="Dataset name to keep"),
        operation: str | None = typer.Option(
            None,
            "--operation",
            help="Further restrict to this operation (e.g. UPDATE)",
        ),
        record_id: str | None = typer.Option(
            None,
            "--record-id",
            help="Further restrict to this record id",
        ),
        store: Path = typer.Option(Path("examples/sample_events.jsonl"), help="Source JSONL store"),
        output: Path = typer.Option(..., "-o", "--output", help="Destination JSONL file"),
    ) -> None:
        """Write events for one dataset to a new JSONL file."""
        source = EventStore(store)
        matches = source.query_events(dataset=dataset, operation=operation, record_id=record_id)
        if not matches:
            console.print(f"[yellow]No events for dataset {dataset}[/yellow]")
            raise typer.Exit(code=1)

        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("w", encoding="utf-8") as fh:
            for event in matches:
                fh.write(event.model_dump_json() + "\n")
        console.print(f"[green]Wrote[/green] {len(matches)} events → {output}")
