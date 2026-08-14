from pydantic import BaseModel, Field


class BoundingBox(BaseModel):
    """Standard bounding box representation."""

    x: int = Field(..., description="Top-left x coordinate")
    y: int = Field(..., description="Top-left y coordinate")
    width: int = Field(..., description="Width of the box")
    height: int = Field(..., description="Height of the box")


class Detection(BaseModel):
    """Object detection result."""

    label: str = Field(..., description="Object class label")
    confidence: float = Field(..., description="Detection confidence (0-1)")
    bbox: BoundingBox = Field(..., description="Object bounding box")


class MotionEvent(BaseModel):
    """Visual motion event."""

    timestamp: float = Field(..., description="Timestamp in seconds")
    magnitude: float = Field(..., description="Weighted magnitude of motion")
    direction: float | None = Field(
        None, description="Primary direction of motion in degrees (0-360)"
    )
    region: BoundingBox | None = Field(
        None, description="Region where motion was detected"
    )


class SceneChange(BaseModel):
    """Scene transition event."""

    timestamp: float = Field(..., description="Timestamp in seconds")
    score: float = Field(..., description="Similarity score change")


class VideoTimeline(BaseModel):
    """Structured timeline of a video for Agentic reasoning."""

    video_path: str
    total_frames: int
    fps: float
    key_frames: list[dict] = Field(
        ..., description="List of frames with paths and detections"
    )


class VisionAnalysis(BaseModel):
    """Result from VLM-based image analysis."""

    source: str = Field(..., description="Analysis source: 'llm' or 'opencv'")
    text: str = Field(..., description="Analytical description or OCR text")
    elements: list[Detection] = Field(
        default_factory=list, description="Detected UI elements (opencv only)"
    )
    model: str | None = Field(
        default=None, description="LLM model used when source='llm'"
    )
    error: str | None = Field(
        default=None, description="Error message if analysis failed"
    )


class FilePath(BaseModel):
    """Value object representing a file path."""

    value: str


class LanguageCode(BaseModel):
    """Value object for OCR language codes (e.g., 'eng')."""

    value: str = "eng"


class TimeSegment(BaseModel):
    """Value object representing a video time segment start and duration."""

    start: float | None = None
    duration: float | None = None


class VideoInfo(BaseModel):
    """Value object representing video metadata information."""

    fps: float
    frame_count: int
    width: int
    height: int


class CommandName(BaseModel):
    """Value object representing a command name."""

    value: str


class CommandOutput(BaseModel):
    """Value object representing JSON command output."""

    value: str


class SceneThreshold(BaseModel):
    """Value object for video scene transition detection threshold."""

    value: float = 30.0


class MinArea(BaseModel):
    """Value object representing minimum pixel area for motion detection."""

    value: int = 500


class AnalysisPrompt(BaseModel):
    """Value object for visual language model prompt."""

    value: str | None = None


class OcrText(BaseModel):
    """Value object representing text extracted via OCR."""

    value: str


class IntervalSeconds(BaseModel):
    """Value object for periodic frame extraction interval."""

    value: float = 1.0


class MaxFrames(BaseModel):
    """Value object for maximum object tracking frame limit."""

    value: int = 300


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
    source: str | None = Field(
        None, description="Analysis source: 'llm' or 'fallback'"
    )
    description: str = Field(..., description="VLM description of the frame")


class VideoUnderstanding(BaseModel):
    """Structured smart video understanding result."""

    video: dict = Field(..., description="Video metadata summary")
    sampling: dict = Field(..., description="Key-frame sampling statistics")
    frames: list[FrameAnalysis] = Field(
        default_factory=list, description="Per key-frame VLM analyses"
    )
    summary: str = Field(..., description="Synthesized video summary")
