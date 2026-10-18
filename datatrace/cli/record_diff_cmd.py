from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console

from datatrace.diff.record_diff import diff_record_events
from datatrace.recorder.store import EventStore

console = Console()


def register_record_diff_command(app: typer.Typer) -> None:
    @app.command("record-diff")
    def record_diff(
        store_a: Path = typer.Argument(..., help="First JSONL store"),
        store_b: Path = typer.Argument(..., help="Second JSONL store"),
        record: str = typer.Option(..., "--record", help="Key=value"),
        json_out: bool = typer.Option(True, "--json/--text", help="JSON output (default)"),
    ) -> None:
        """Diff transformation events for one record across two stores."""
        if "=" not in record:
            raise typer.BadParameter("Use --record key=value")
        record_id = record.split("=", 1)[1]
        diff = diff_record_events(EventStore(store_a), EventStore(store_b), record_id)
        if not diff.only_in_a and not diff.only_in_b and not diff.changed:
            console.print("[yellow]No differences for this record.[/yellow]")
            raise typer.Exit(code=0)
        if json_out:
            console.print(
                json.dumps(
                    {
                        "record_id": record_id,
                        "only_in_a": [e.model_dump(mode="json") for e in diff.only_in_a],
                        "only_in_b": [e.model_dump(mode="json") for e in diff.only_in_b],
                        "changed": [
                            {
                                "a": a.model_dump(mode="json"),
                                "b": b.model_dump(mode="json"),
                            }
                            for a, b in diff.changed
                        ],
                    },
                    indent=2,
                    default=str,
                ),
            )
            return
        console.print(f"Only in A: {len(diff.only_in_a)}, only in B: {len(diff.only_in_b)}")
        console.print(f"Changed pairs: {len(diff.changed)}")
