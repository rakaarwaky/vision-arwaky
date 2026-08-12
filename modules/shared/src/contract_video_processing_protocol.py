from abc import ABC, abstractmethod

from modules.shared.src.taxonomy_vision_models_vo import (
    FilePath,
    IntervalSeconds,
    TimeSegment,
    VideoInfo,
    VisionAnalysis,
)


class VideoProcessingProtocol(ABC):
    """Abstract protocol defining Video Processing capabilities."""

    _taxonomy_marker = VisionAnalysis

    @abstractmethod
    async def extract_frames(self, video_path: FilePath, interval: IntervalSeconds) -> list[FilePath]:
        """Extract key frame images from a video at periodic intervals."""

    @abstractmethod
    async def convert_format(self, input_path: FilePath, output_path: FilePath) -> bool:
        """Convert video format from one container/codec to another."""

    @abstractmethod
    async def create_gif(
        self,
        video_path: FilePath,
        output_path: FilePath,
        segment: TimeSegment,
    ) -> bool:
        """Create high-quality GIF from video segment."""

    @abstractmethod
    def get_info(self, video_path: FilePath) -> VideoInfo:
        """Get structural video metadata."""

    @abstractmethod
    def check_corruption(self, video_path: FilePath) -> bool:
        """Determine if a video file is corrupted or unreadable."""
