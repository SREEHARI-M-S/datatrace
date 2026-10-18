import json
from pathlib import Path

from datatrace.diff.record_diff import diff_record_events
from datatrace.models.events import TransformationEvent
from datatrace.recorder.store import EventStore


def test_record_diff_detects_after_change(tmp_path: Path) -> None:
    base = {
        "record_id": "9",
        "dataset": "identity_mapping",
        "timestamp": "2026-01-01T00:00:00Z",
        "operation": "UPDATE",
        "before": {"identity_id": "a"},
        "after": {"identity_id": "b"},
        "transformation": "identity_mapping.sql",
    }
    a = tmp_path / "a.jsonl"
    b = tmp_path / "b.jsonl"
    a.write_text(json.dumps(base) + "\n", encoding="utf-8")
    changed = dict(base)
    changed["after"] = {"identity_id": "c"}
    b.write_text(json.dumps(changed) + "\n", encoding="utf-8")
    diff = diff_record_events(EventStore(a), EventStore(b), "9")
    assert len(diff.changed) == 1
