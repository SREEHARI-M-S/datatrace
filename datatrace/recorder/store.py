from __future__ import annotations

import json
from pathlib import Path

from datatrace.models.events import TransformationEvent


class EventStore:
    def __init__(self, path: Path) -> None:
        self._path = path

    def append(self, event: TransformationEvent) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._path.open("a", encoding="utf-8") as fh:
            fh.write(event.model_dump_json() + "\n")

    def load_for_record(self, record_id: str) -> list[TransformationEvent]:
        if not self._path.is_file():
            return []
        events: list[TransformationEvent] = []
        with self._path.open(encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                event = TransformationEvent.model_validate_json(line)
                if event.record_id == record_id:
                    events.append(event)
        events.sort(key=lambda e: e.timestamp)
        return events

    def iter_events(self) -> list[TransformationEvent]:
        if not self._path.is_file():
            return []
        events: list[TransformationEvent] = []
        with self._path.open(encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                events.append(TransformationEvent.model_validate_json(line))
        return events

    def list_record_ids(self) -> list[str]:
        return sorted({e.record_id for e in self.iter_events()})

    def stats(self) -> dict[str, int]:
        events = self.iter_events()
        record_ids = {e.record_id for e in events}
        datasets = {e.dataset for e in events}
        return {
            "events": len(events),
            "records": len(record_ids),
            "datasets": len(datasets),
        }
