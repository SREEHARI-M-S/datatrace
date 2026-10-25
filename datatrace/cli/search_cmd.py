from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console

from datatrace.recorder.store import EventStore

console = Console()


def register_search_command(app: typer.Typer) -> None:
    @app.command("search")
    def search(
        query: str = typer.Argument(..., help="Substring to match in dataset, operation, or transformation"),
        store: Path = typer.Option(Path("examples/sample_events.jsonl"), help="JSONL store"),
        record_id: str | None = typer.Option(None, "--record-id", help="Only search within this record"),
        json_out: bool = typer.Option(True, "--json/--text", help="JSON output (default)"),
        output: Path | None = typer.Option(None, "-o", "--output", help="Write matching events JSON to file"),
    ) -> None:
        """Find events whose dataset, operation, or transformation contains the query."""
        needle = query.lower()
        source = EventStore(store).query_events(record_id=record_id) if record_id else EventStore(store).iter_events()
        hits = [
            event
            for event in source
            if needle in event.dataset.lower()
            or needle in event.operation.lower()
            or needle in event.transformation.lower()
        ]
        if not hits:
            console.print("[yellow]No matching events.[/yellow]")
            raise typer.Exit(code=1)
        payload = [e.model_dump(mode="json") for e in hits]
        if output is not None:
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
            console.print(f"[green]Wrote[/green] {output}")
        if json_out:
            console.print(json.dumps(payload, indent=2, default=str))
            return
        if output is not None:
            return
        for event in hits:
            console.print(f"{event.record_id} {event.dataset} {event.operation}")
