from pathlib import Path

from datatrace.recorder.store import EventStore


def test_stats_on_sample_events() -> None:
    store = EventStore(Path("examples/sample_events.jsonl"))
    summary = store.stats()
    assert summary["events"] == 3
    assert summary["records"] == 1
    assert summary["datasets"] == 3
