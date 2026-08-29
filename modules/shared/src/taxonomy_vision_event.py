"""Domain events for visual scene transitions and motion occurrences."""

from __future__ import annotations

from pydantic import BaseModel, Field

from modules.shared.src.taxonomy_vision_vo import BoundingBox


class MotionEvent(BaseModel):
    """Visual motion event occurrence."""

    timestamp: float = Field(..., description="Timestamp in seconds")
    magnitude: float = Field(..., description="Weighted magnitude of motion")
    direction: float | None = Field(
        None, description="Primary direction of motion in degrees (0-360)"
    )
    region: BoundingBox | None = Field(
        None, description="Region where motion was detected"
    )


class SceneChange(BaseModel):
    """Scene transition event occurrence."""

    timestamp: float = Field(..., description="Timestamp in seconds")
    score: float = Field(..., description="Similarity score change")
