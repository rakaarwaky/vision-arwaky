"""Video processing protocol contract."""

from abc import ABC, abstractmethod
from typing import List

from modules.shared.src.common.taxonomy_common_vo import FilePath
from modules.shared.src.video.taxonomy_video_vo import (
    IntervalSeconds,
    MaxFrames,
    MinArea,
    MotionEvent,
    SceneChange,
    SceneThreshold,
    TimeSegment,
    VideoInfo,
    VideoTimeline,
)


class VideoProcessingProtocol(ABC):
    """Abstract protocol for video processing capabilities."""

    @abstractmethod
    async def extract_frames(self, video_path: FilePath, interval: IntervalSeconds) -> List[FilePath]:
        """Extract frames from video at specific interval."""
        ...

    @abstractmethod
    async def convert_format(self, input_path: FilePath, output_path: FilePath) -> bool:
        """Convert video format using FFmpeg."""
        ...

    @abstractmethod
    async def create_gif(
        self,
        video_path: FilePath,
        output_path: FilePath,
        segment: TimeSegment,
    ) -> bool:
        """Create high-quality GIF from video segment."""
        ...

    @abstractmethod
    def get_info(self, video_path: FilePath) -> VideoInfo:
        """Get video metadata using OpenCV."""
        ...

    @abstractmethod
    def check_corruption(self, video_path: FilePath) -> bool:
        """Check if video file is corrupted."""
        ...


class VideoAnalysisProtocol(ABC):
    """Abstract protocol for video analysis capabilities."""

    @abstractmethod
    def detect_scenes(self, video_path: FilePath, threshold: SceneThreshold) -> List[SceneChange]:
        """Detect scene changes by comparing consecutive frame histograms."""
        ...

    @abstractmethod
    def detect_motion(self, video_path: FilePath, min_area: MinArea) -> List[MotionEvent]:
        """Detect significant motion events using frame differencing."""
        ...


class ObjectTrackingProtocol(ABC):
    """Abstract protocol for object tracking capabilities."""

    @abstractmethod
    def track_object(
        self,
        video_path: FilePath,
        initial_box: "BoundingBox",
        max_frames: MaxFrames,
    ) -> List["BoundingBox"]:
        """Track an object starting from an initial bounding box."""
        ...


class VideoTimelineProtocol(ABC):
    """Abstract protocol for video timeline generation."""

    @abstractmethod
    async def generate_timeline(self, video_path: FilePath, interval: IntervalSeconds) -> VideoTimeline:
        """Generate a structured timeline of the video."""
        ...
