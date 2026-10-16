from __future__ import annotations

from pydantic import BaseModel, Field

from datatrace.recorder.store import EventStore


class StoreDiffSummary(BaseModel):
    only_in_a: list[str] = Field(default_factory=list)
    only_in_b: list[str] = Field(default_factory=list)
    in_both: list[str] = Field(default_factory=list)


def diff_record_ids(store_a: EventStore, store_b: EventStore) -> StoreDiffSummary:
    ids_a = set(store_a.list_record_ids())
    ids_b = set(store_b.list_record_ids())
    return StoreDiffSummary(
        only_in_a=sorted(ids_a - ids_b),
        only_in_b=sorted(ids_b - ids_a),
        in_both=sorted(ids_a & ids_b),
    )
