from abc import ABC, abstractmethod
from typing import List
from src.shared.vision_models_vo import FilePath, TimeSegment, VisionAnalysis, IntervalSeconds, VideoInfo


class VideoProcessingProtocol(ABC):
    """Abstract protocol defining Video Processing capabilities."""

    _taxonomy_marker = VisionAnalysis

    @abstractmethod
    async def extract_frames(self, video_path: FilePath, interval: IntervalSeconds) -> List[FilePath]:
        """Extract key frame images from a video at periodic intervals."""
        pass

    @abstractmethod
    async def convert_format(self, input_path: FilePath, output_path: FilePath) -> bool:
        """Convert video format from one container/codec to another."""
        pass

    @abstractmethod
    async def create_gif(
        self,
        video_path: FilePath,
        output_path: FilePath,
        segment: TimeSegment,
    ) -> bool:
        """Create high-quality GIF from video segment."""
        pass

    @abstractmethod
    def get_info(self, video_path: FilePath) -> VideoInfo:
        """Get structural video metadata."""
        pass

    @abstractmethod
    def check_corruption(self, video_path: FilePath) -> bool:
        """Determine if a video file is corrupted or unreadable."""
        pass
