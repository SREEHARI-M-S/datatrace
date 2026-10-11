from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console

from datatrace.models.events import TransformationEvent
from datatrace.recorder.store import EventStore

console = Console()


def register_ingest_command(app: typer.Typer) -> None:
    @app.command("ingest")
    def ingest(
        store: Path = typer.Option(
            Path("events.jsonl"),
            help="JSONL event store to append to",
        ),
        event_json: Path | None = typer.Option(
            None,
            "--file",
            help="JSON file containing one event object",
        ),
    ) -> None:
        """Append a transformation event to a JSONL store."""
        if event_json is None:
            console.print("Provide --file with a JSON event payload.")
            raise typer.Exit(code=1)

        payload = json.loads(event_json.read_text(encoding="utf-8"))
        event = TransformationEvent.model_validate(payload)
        EventStore(store).append(event)
        console.print(f"[green]Appended[/green] record {event.record_id} → {event.dataset}")
