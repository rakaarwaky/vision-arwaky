"""Value objects and domain data models for vision operations."""

from __future__ import annotations

from pydantic import BaseModel, Field

from modules.shared.src.taxonomy_vision_constant import (
    ANALYZE_VIDEO_INTERVAL_S,
    MIN_MOTION_AREA,
    SCENE_THRESHOLD,
    TOP_MOTION_EVENTS_LIMIT,
)

# pylint: disable=too-few-public-methods


class BoundingBox(BaseModel):
    """Standard bounding box representation."""

    x: int = Field(..., description="Top-left x coordinate")
    y: int = Field(..., description="Top-left y coordinate")
    width: int = Field(..., description="Width of the box")
    height: int = Field(..., description="Height of the box")


class VisionAnalysis(BaseModel):
    """Result from VLM-based image analysis."""

    source: str = Field(..., description="Analysis source: 'llm' or 'opencv'")
    text: str = Field(..., description="Analytical description or OCR text")
    model: str | None = Field(
        default=None, description="LLM model used when source='llm'"
    )
    error: str | None = Field(
        default=None, description="Error message if analysis failed"
    )


class FilePath(BaseModel):
    """Value object representing a validated file path."""

    value: str


class LanguageCode(BaseModel):
    """Value object for OCR language codes (e.g., 'eng')."""

    value: str = "eng"


class VideoInfo(BaseModel):
    """Value object representing video metadata information."""

    fps: float
    frame_count: int
    width: int
    height: int


class CommandName(BaseModel):
    """Value object representing a command name."""

    value: str


class ConfigKey(BaseModel):
    """Value object representing a configuration key."""

    value: str = ""


class CommandOutput(BaseModel):
    """Value object representing JSON command output."""

    value: str


class SceneThreshold(BaseModel):
    """Value object for video scene transition detection threshold."""

    value: float = Field(default=30.0, gt=0)


class MinArea(BaseModel):
    """Value object representing minimum pixel area for motion detection."""

    value: int = Field(default=500, gt=0)


class AnalysisPrompt(BaseModel):
    """Value object for visual language model prompt."""

    value: str | None = None


class OcrText(BaseModel):
    """Value object representing text extracted via OCR."""

    value: str


class IntervalSeconds(BaseModel):
    """Value object for periodic frame extraction interval."""

    value: float = Field(default=1.0, gt=0)


class MaxFrames(BaseModel):
    """Value object for maximum object tracking frame limit."""

    value: int = Field(default=300, gt=0)


class BackendType(BaseModel):
    """Value object for the active VLM backend type ('external')."""

    value: str = "external"


class ModelName(BaseModel):
    """Value object for the active VLM model name."""

    value: str


class ScreenshotComparison(BaseModel):
    """Result of comparing two screenshots."""

    identical: bool
    phash_diff: bool
    differences: list[BoundingBox] = Field(default_factory=list)


class FrameAnalysis(BaseModel):
    """VLM description of a single sampled key frame."""

    frame: int = Field(..., description="1-based index in the extracted frame list")
    timestamp_s: float = Field(..., description="Timestamp in seconds")
    source: str | None = Field(None, description="Analysis source: 'llm' or 'fallback'")
    description: str = Field(..., description="VLM description of the frame")


class VideoUnderstanding(BaseModel):
    """Structured smart video understanding result."""

    video: dict = Field(..., description="Video metadata summary")
    sampling: dict = Field(..., description="Key-frame sampling statistics")
    frames: list[FrameAnalysis] = Field(
        default_factory=list, description="Per key-frame VLM analyses"
    )
    summary: str = Field(..., description="Synthesized analytical summary")


class VideoUnderstandingConfig(BaseModel):
    """Tuning parameters for key-frame selection and VLM analysis.

    Bundles the optional sampling thresholds so the understanding capability
    exposes a small, stable ``analyze`` signature instead of many positional
    arguments.
    """

    interval: float = ANALYZE_VIDEO_INTERVAL_S
    scene_threshold: float = SCENE_THRESHOLD
    min_area: int = MIN_MOTION_AREA
    top_motion: int = TOP_MOTION_EVENTS_LIMIT


class Timestamp(BaseModel):
    """Value object representing a video timestamp in seconds."""

    value: float


class MotionMagnitude(BaseModel):
    """Value object representing motion magnitude."""

    value: float


class MotionDirection(BaseModel):
    """Value object representing motion direction in degrees."""

    value: float


class SimilarityScore(BaseModel):
    """Value object representing similarity score change."""

    value: float
