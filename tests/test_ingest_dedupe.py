from pathlib import Path

from datatrace.models.events import TransformationEvent
from datatrace.recorder.store import EventStore


def _sample_event(record_id: str = "1") -> TransformationEvent:
    return TransformationEvent(
        record_id=record_id,
        dataset="raw",
        timestamp="2024-01-01T00:00:00",
        operation="load",
        transformation="ingest",
    )


def test_existing_raw_lines_and_dedupe_merge(tmp_path: Path) -> None:
    store_path = tmp_path / "events.jsonl"
    store = EventStore(store_path)
    store.append(_sample_event())
    line = store_path.read_text(encoding="utf-8").strip()
    assert line in store.existing_raw_lines()

    merge_path = tmp_path / "merge.jsonl"
    merge_path.write_text(line + "\n" + _sample_event("2").model_dump_json() + "\n", encoding="utf-8")

    existing = store.existing_raw_lines()
    appended = 0
    skipped = 0
    for raw in merge_path.read_text(encoding="utf-8").splitlines():
        raw = raw.strip()
        if not raw:
            continue
        if raw in existing:
            skipped += 1
            continue
        store.append(TransformationEvent.model_validate_json(raw))
        existing.add(raw)
        appended += 1
    assert skipped == 1
    assert appended == 1
    assert len(store.iter_events()) == 2
