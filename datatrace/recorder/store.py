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

    def events_for_dataset(self, dataset: str) -> list[TransformationEvent]:
        return [e for e in self.iter_events() if e.dataset == dataset]

    def query_events(
        self,
        *,
        dataset: str | None = None,
        operation: str | None = None,
        record_id: str | None = None,
    ) -> list[TransformationEvent]:
        events = self.iter_events()
        if dataset is not None:
            events = [e for e in events if e.dataset == dataset]
        if operation is not None:
            events = [e for e in events if e.operation == operation]
        if record_id is not None:
            events = [e for e in events if e.record_id == record_id]
        return events

    def list_record_ids(self, dataset: str | None = None) -> list[str]:
        events = self.iter_events()
        if dataset is not None:
            events = [e for e in events if e.dataset == dataset]
        return sorted({e.record_id for e in events})

    def stats(self) -> dict[str, int]:
        events = self.iter_events()
        record_ids = {e.record_id for e in events}
        datasets = {e.dataset for e in events}
        return {
            "events": len(events),
            "records": len(record_ids),
            "datasets": len(datasets),
        }

    def events_per_dataset(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for event in self.iter_events():
            counts[event.dataset] = counts.get(event.dataset, 0) + 1
        return dict(sorted(counts.items()))

    def events_per_operation(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for event in self.iter_events():
            counts[event.operation] = counts.get(event.operation, 0) + 1
        return dict(sorted(counts.items()))

    def list_operations(self) -> list[str]:
        return sorted({e.operation for e in self.iter_events()})

    def list_transformations(self) -> list[str]:
        return sorted({e.transformation for e in self.iter_events()})

    def existing_raw_lines(self) -> set[str]:
        if not self._path.is_file():
            return set()
        return {line.strip() for line in self._path.read_text(encoding="utf-8").splitlines() if line.strip()}
