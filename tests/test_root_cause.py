from datetime import datetime, timezone

from datatrace.analysis.root_cause import first_significant_change
from datatrace.models.events import TransformationEvent


def test_first_change() -> None:
    events = [
        TransformationEvent(
            record_id="1",
            dataset="a",
            timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc),
            operation="INSERT",
            before={},
            after={"x": 1},
            transformation="a.sql",
        ),
        TransformationEvent(
            record_id="1",
            dataset="b",
            timestamp=datetime(2026, 1, 2, tzinfo=timezone.utc),
            operation="UPDATE",
            before={"identity_id": "abc122"},
            after={"identity_id": "abc123"},
            transformation="identity_mapping.sql",
        ),
    ]
    finding = first_significant_change(events)
    assert finding is not None
    assert finding.transformation == "identity_mapping.sql"
