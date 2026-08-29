"""Domain events for visual scene transitions and motion occurrences."""

from __future__ import annotations

from pydantic import BaseModel, Field

from modules.shared.src.taxonomy_vision_vo import (
    BoundingBox,
    MotionDirection,
    MotionMagnitude,
    SimilarityScore,
    Timestamp,
)


class MotionEvent(BaseModel):
    """Visual motion event occurrence."""

    timestamp: Timestamp = Field(..., description="Timestamp in seconds")
    magnitude: MotionMagnitude = Field(..., description="Weighted magnitude of motion")
    direction: MotionDirection | None = Field(
        None, description="Primary direction of motion in degrees (0-360)"
    )
    region: BoundingBox | None = Field(
        None, description="Region where motion was detected"
    )


class SceneChange(BaseModel):
    """Scene transition event occurrence."""

    timestamp: Timestamp = Field(..., description="Timestamp in seconds")
    score: SimilarityScore = Field(..., description="Similarity score change")
