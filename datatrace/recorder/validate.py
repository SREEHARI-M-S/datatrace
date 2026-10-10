from __future__ import annotations

from pathlib import Path

from pydantic import ValidationError

from datatrace.models.events import TransformationEvent


class ValidationIssue:
    def __init__(self, line: int, message: str) -> None:
        self.line = line
        self.message = message


def validate_event_store(path: Path) -> list[ValidationIssue]:
    if not path.is_file():
        return [ValidationIssue(0, f"File not found: {path}")]

    issues: list[ValidationIssue] = []
    with path.open(encoding="utf-8") as fh:
        for line_no, line in enumerate(fh, start=1):
            text = line.strip()
            if not text:
                continue
            try:
                TransformationEvent.model_validate_json(text)
            except ValidationError as exc:
                issues.append(ValidationIssue(line_no, str(exc.errors()[0]["msg"])))
    return issues
