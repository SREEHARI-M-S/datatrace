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
        merge_jsonl: Path | None = typer.Option(
            None,
            "--merge",
            help="Append all events from another JSONL file",
        ),
        dedupe: bool = typer.Option(
            False,
            "--dedupe",
            help="When merging, skip lines identical to an existing store line",
        ),
        json_out: bool = typer.Option(False, "--json", help="Print merge summary as JSON"),
    ) -> None:
        """Append transformation event(s) to a JSONL store."""
        target = EventStore(store)
        if merge_jsonl is not None:
            existing = target.existing_raw_lines() if dedupe else set()
            count = 0
            skipped = 0
            for line in merge_jsonl.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line:
                    continue
                if dedupe and line in existing:
                    skipped += 1
                    continue
                target.append(TransformationEvent.model_validate_json(line))
                if dedupe:
                    existing.add(line)
                count += 1
            if json_out:
                console.print(
                    json.dumps(
                        {
                            "store": str(store),
                            "merged": count,
                            "skipped_duplicates": skipped if dedupe else 0,
                        },
                        indent=2,
                    ),
                )
            else:
                msg = f"[green]Merged[/green] {count} events into {store}"
                if dedupe and skipped:
                    msg += f" ({skipped} duplicate lines skipped)"
                console.print(msg)
            raise typer.Exit(code=0)
        if event_json is None:
            console.print("Provide --file or --merge.")
            raise typer.Exit(code=1)

        payload = json.loads(event_json.read_text(encoding="utf-8"))
        event = TransformationEvent.model_validate(payload)
        target.append(event)
        console.print(f"[green]Appended[/green] record {event.record_id} → {event.dataset}")
