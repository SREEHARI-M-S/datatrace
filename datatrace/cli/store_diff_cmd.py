from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console

from datatrace.diff.store_diff import diff_record_ids
from datatrace.recorder.store import EventStore

console = Console()


def register_store_diff_command(app: typer.Typer) -> None:
    @app.command("diff-stores")
    def diff_stores(
        store_a: Path = typer.Argument(..., help="First JSONL store"),
        store_b: Path = typer.Argument(..., help="Second JSONL store"),
        json_out: bool = typer.Option(False, "--json", help="Print JSON summary"),
    ) -> None:
        """Compare record IDs present in two event stores."""
        summary = diff_record_ids(EventStore(store_a), EventStore(store_b))
        if json_out:
            console.print(json.dumps(summary.model_dump(), indent=2))
            return
        console.print(f"Only in A: {len(summary.only_in_a)}")
        console.print(f"Only in B: {len(summary.only_in_b)}")
        console.print(f"In both: {len(summary.in_both)}")
