from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class TransformationEvent(BaseModel):
    record_id: str
    dataset: str
    timestamp: datetime
    operation: str
    before: dict[str, Any] = Field(default_factory=dict)
    after: dict[str, Any] = Field(default_factory=dict)
    transformation: str
