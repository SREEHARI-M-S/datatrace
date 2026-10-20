from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from datatrace.analysis.audit import audit_records
from datatrace.recorder.store import EventStore

console = Console()


def register_audit_command(app: typer.Typer) -> None:
    @app.command("audit")
    def audit(
        store: Path = typer.Option(Path("examples/sample_events.jsonl"), help="JSONL event store"),
        json_out: bool = typer.Option(False, "--json", help="Print audit rows as JSON"),
        only_changed: bool = typer.Option(
            False,
            "--only-changed",
            help="List only records with a detected root cause",
        ),
    ) -> None:
        """Scan the store and report per-record event counts and root-cause hints."""
        rows = audit_records(EventStore(store))
        if only_changed:
            rows = [row for row in rows if row.root_cause is not None]
        if not rows:
            console.print("[yellow]No records to audit.[/yellow]")
            raise typer.Exit(code=1)

        if json_out:
            payload = [
                {
                    "record_id": row.record_id,
                    "event_count": row.event_count,
                    "root_cause": (
                        {
                            "summary": row.root_cause.summary,
                            "transformation": row.root_cause.transformation,
                            "evidence": row.root_cause.evidence,
                        }
                        if row.root_cause
                        else None
                    ),
                }
                for row in rows
            ]
            console.print(json.dumps(payload, indent=2, default=str))
            return

        table = Table(title="Record audit")
        table.add_column("Record")
        table.add_column("Events", justify="right")
        table.add_column("Root cause")
        table.add_column("Transformation")
        for row in rows:
            if row.root_cause:
                table.add_row(
                    row.record_id,
                    str(row.event_count),
                    row.root_cause.summary,
                    row.root_cause.transformation,
                )
            else:
                table.add_row(row.record_id, str(row.event_count), "—", "—")
        console.print(table)
