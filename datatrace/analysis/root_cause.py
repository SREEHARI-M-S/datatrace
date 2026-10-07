from __future__ import annotations

from datatrace.models.events import TransformationEvent


class RootCauseFinding:
    def __init__(
        self,
        transformation: str,
        summary: str,
        evidence: dict[str, object],
    ) -> None:
        self.transformation = transformation
        self.summary = summary
        self.evidence = evidence


def first_significant_change(events: list[TransformationEvent]) -> RootCauseFinding | None:
    """Prefer UPDATE events where existing fields changed; fall back to any state change."""
    for event in events:
        if event.operation == "UPDATE" and event.before != event.after:
            return _finding(event)
    for event in events:
        if event.before != event.after:
            return _finding(event)
    return None


def _finding(event: TransformationEvent) -> RootCauseFinding:
    return RootCauseFinding(
        transformation=event.transformation,
        summary=f"Value changed in {event.dataset}",
        evidence={"before": event.before, "after": event.after, "operation": event.operation},
    )
