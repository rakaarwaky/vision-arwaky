"""Value objects and domain data models for vision operations."""

from __future__ import annotations

from pydantic import BaseModel, Field

from modules.shared.src.common.taxonomy_vision_constant import (
    ANALYZE_VIDEO_INTERVAL_S,
)

# pylint: disable=too-few-public-methods


class VisionAnalysis(BaseModel):
    """Result from VLM-based image analysis."""

    source: str = Field(..., description="Analysis source: 'llm' or 'opencv'")
    text: str = Field(..., description="Analytical description")
    model: str | None = Field(
        default=None, description="LLM model used when source='llm'"
    )
    error: str | None = Field(
        default=None, description="Error message if analysis failed"
    )


class FilePath(BaseModel):
    """Value object representing a validated file path."""

    value: str

    @classmethod
    def from_str(cls, value: str) -> FilePath:
        """Build a FilePath from a raw string."""
        return cls(value=value)

    @classmethod
    def from_pathlib(cls, p: object) -> FilePath:
        """Build a FilePath from a pathlib.Path."""
        return cls(value=str(p))


class CommandName(BaseModel):
    """Value object representing a command name."""

    value: str


class ConfigKey(BaseModel):
    """Value object representing a configuration key."""

    value: str = ""


class SystemCommandParams(BaseModel):
    """Typed parameter payload for system command handlers."""

    model_config = {"extra": "allow"}

    target_dir: str = "."
    key: str = ""
    value: object | None = None
    job_id: str = ""


class CommandOutput(BaseModel):
    """Value object representing JSON command output."""

    value: str


class AnalysisPrompt(BaseModel):
    """Value object for visual language model prompt."""

    value: str | None = None


class BackendType(BaseModel):
    """Value object for the active VLM backend type ('external')."""

    value: str = "external"


class ModelName(BaseModel):
    """Value object for the active VLM model name."""

    value: str


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
    """Tuning parameters for key-frame selection and VLM analysis."""

    interval: float = ANALYZE_VIDEO_INTERVAL_S
