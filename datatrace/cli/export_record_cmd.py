from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console

from datatrace.analysis.root_cause import first_significant_change
from datatrace.recorder.store import EventStore
from datatrace.trace.record_tracer import build_lineage

console = Console()


def register_export_record_command(app: typer.Typer) -> None:
    @app.command("export-record")
    def export_record(
        record: str = typer.Option(..., "--record", help="Key=value"),
        store: Path = typer.Option(Path("examples/sample_events.jsonl"), help="JSONL store"),
        output: Path = typer.Option(..., "-o", "--output", help="Write JSON bundle"),
    ) -> None:
        """Export events, lineage, and root-cause summary for one record."""
        if "=" not in record:
            raise typer.BadParameter("Use --record key=value")
        record_id = record.split("=", 1)[1]
        events = EventStore(store).load_for_record(record_id)
        if not events:
            console.print("[yellow]No events found.[/yellow]")
            raise typer.Exit(code=1)

        lineage = build_lineage(events)
        finding = first_significant_change(events)
        payload: dict[str, object] = {
            "record_id": record_id,
            "events": [e.model_dump(mode="json") for e in events],
            "lineage": [{"dataset": d, "state": s} for d, s in lineage],
        }
        if finding:
            payload["root_cause"] = {
                "summary": finding.summary,
                "transformation": finding.transformation,
                "evidence": finding.evidence,
            }

        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
        console.print(f"[green]Wrote[/green] {output}")
