from __future__ import annotations

from typing import Any

from datatrace.models.events import TransformationEvent


def trace_column(events: list[TransformationEvent], column: str) -> list[dict[str, Any]]:
    """Return chronological values for one column across transformation events."""
    trail: list[dict[str, Any]] = []
    for event in events:
        value = event.after.get(column)
        if column in event.after or column in event.before:
            trail.append(
                {
                    "dataset": event.dataset,
                    "timestamp": event.timestamp.isoformat(),
                    "value": value,
                    "transformation": event.transformation,
                },
            )
    return trail
