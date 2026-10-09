from __future__ import annotations

from typing import Any


def diff_fields(before: dict[str, Any], after: dict[str, Any]) -> list[tuple[str, Any, Any]]:
    """Return (field, old_value, new_value) for keys whose values differ."""
    keys = set(before) | set(after)
    changes: list[tuple[str, Any, Any]] = []
    for key in sorted(keys):
        old = before.get(key)
        new = after.get(key)
        if old != new:
            changes.append((key, old, new))
    return changes
