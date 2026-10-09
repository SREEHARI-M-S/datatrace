from datatrace.trace.changed_fields import diff_fields


def test_diff_fields() -> None:
    changes = diff_fields({"identity_id": "abc122"}, {"identity_id": "abc123"})
    assert changes == [("identity_id", "abc122", "abc123")]
