from __future__ import annotations

from pydantic import BaseModel, Field

from datatrace.recorder.store import EventStore


class StoreDiffSummary(BaseModel):
    only_in_a: list[str] = Field(default_factory=list)
    only_in_b: list[str] = Field(default_factory=list)
    in_both: list[str] = Field(default_factory=list)
    dataset_counts_a: dict[str, int] = Field(default_factory=dict)
    dataset_counts_b: dict[str, int] = Field(default_factory=dict)


def dataset_event_counts(store: EventStore) -> dict[str, int]:
    counts: dict[str, int] = {}
    for event in store.iter_events():
        counts[event.dataset] = counts.get(event.dataset, 0) + 1
    return counts


def diff_record_ids(store_a: EventStore, store_b: EventStore) -> StoreDiffSummary:
    ids_a = set(store_a.list_record_ids())
    ids_b = set(store_b.list_record_ids())
    return StoreDiffSummary(
        only_in_a=sorted(ids_a - ids_b),
        only_in_b=sorted(ids_b - ids_a),
        in_both=sorted(ids_a & ids_b),
        dataset_counts_a=dataset_event_counts(store_a),
        dataset_counts_b=dataset_event_counts(store_b),
    )
