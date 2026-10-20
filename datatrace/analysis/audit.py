from __future__ import annotations

from dataclasses import dataclass

from datatrace.analysis.root_cause import RootCauseFinding, first_significant_change
from datatrace.recorder.store import EventStore


@dataclass(frozen=True)
class RecordAudit:
    record_id: str
    event_count: int
    root_cause: RootCauseFinding | None


def audit_records(store: EventStore) -> list[RecordAudit]:
    """Summarize each record's event volume and first significant data change."""
    results: list[RecordAudit] = []
    for record_id in store.list_record_ids():
        events = store.load_for_record(record_id)
        results.append(
            RecordAudit(
                record_id=record_id,
                event_count=len(events),
                root_cause=first_significant_change(events),
            ),
        )
    return results
