from __future__ import annotations

from pydantic import BaseModel, Field

from datatrace.models.events import TransformationEvent
from datatrace.recorder.store import EventStore


class RecordEventDiff(BaseModel):
    only_in_a: list[TransformationEvent] = Field(default_factory=list)
    only_in_b: list[TransformationEvent] = Field(default_factory=list)
    changed: list[tuple[TransformationEvent, TransformationEvent]] = Field(default_factory=list)


def _event_key(event: TransformationEvent) -> tuple[str, str, str]:
    return (event.dataset, event.operation, event.transformation)


def diff_record_events(store_a: EventStore, store_b: EventStore, record_id: str) -> RecordEventDiff:
    events_a = store_a.load_for_record(record_id)
    events_b = store_b.load_for_record(record_id)
    keys_a = {_event_key(e): e for e in events_a}
    keys_b = {_event_key(e): e for e in events_b}

    only_a = [e for k, e in keys_a.items() if k not in keys_b]
    only_b = [e for k, e in keys_b.items() if k not in keys_a]
    changed: list[tuple[TransformationEvent, TransformationEvent]] = []
    for key in keys_a:
        if key not in keys_b:
            continue
        if keys_a[key].after != keys_b[key].after or keys_a[key].before != keys_b[key].before:
            changed.append((keys_a[key], keys_b[key]))
    return RecordEventDiff(only_in_a=only_a, only_in_b=only_b, changed=changed)
