from __future__ import annotations

from datatrace.models.events import TransformationEvent


def timeline_report_markdown(record_id: str, events: list[TransformationEvent]) -> str:
    lines = [
        "# DataTrace timeline",
        "",
        f"**Record:** `{record_id}`",
        "",
        "| Time | Dataset | Operation | Transformation |",
        "| --- | --- | --- | --- |",
    ]
    for event in events:
        lines.append(
            f"| {event.timestamp.isoformat()} | `{event.dataset}` | {event.operation} | `{event.transformation}` |",
        )
    return "\n".join(lines) + "\n"
