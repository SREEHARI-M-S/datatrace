from __future__ import annotations

from pathlib import Path

from datatrace.models.events import TransformationEvent


class ChronologyIssue:
    def __init__(self, record_id: str, message: str) -> None:
        self.record_id = record_id
        self.message = message


def validate_chronology(path: Path) -> list[ChronologyIssue]:
    if not path.is_file():
        return [ChronologyIssue("", f"File not found: {path}")]

    by_record: dict[str, list[TransformationEvent]] = {}
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            text = line.strip()
            if not text:
                continue
            event = TransformationEvent.model_validate_json(text)
            by_record.setdefault(event.record_id, []).append(event)

    issues: list[ChronologyIssue] = []
    for record_id, events in by_record.items():
        ordered = sorted(events, key=lambda e: e.timestamp)
        for prev, curr in zip(ordered, ordered[1:]):
            if curr.timestamp < prev.timestamp:
                issues.append(
                    ChronologyIssue(
                        record_id,
                        f"Timestamp goes backwards between {prev.dataset} and {curr.dataset}",
                    ),
                )
                break
    return issues
