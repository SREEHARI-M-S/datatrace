from __future__ import annotations

from datatrace.models.events import TransformationEvent


def build_lineage(events: list[TransformationEvent]) -> list[tuple[str, dict[str, object]]]:
    return [(e.dataset, e.after) for e in events]
