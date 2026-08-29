from abc import ABC, abstractmethod

from modules.shared.src.taxonomy_vision_vo import (
    FilePath,
    IntervalSeconds,
    VideoInfo,
    VisionAnalysis,
)


class VideoProcessingProtocol(ABC):
    """Abstract protocol defining Video Processing capabilities."""

    _taxonomy_marker = VisionAnalysis

    @abstractmethod
    async def extract_frames(
        self, video_path: FilePath, interval: IntervalSeconds
    ) -> list[FilePath]:
        """Extract key frame images from a video at periodic intervals."""

    @abstractmethod
    def get_info(self, video_path: FilePath) -> VideoInfo:
        """Get structural video metadata."""

    @abstractmethod
    def check_corruption(self, video_path: FilePath) -> bool:
        """Determine if a video file is corrupted or unreadable."""
