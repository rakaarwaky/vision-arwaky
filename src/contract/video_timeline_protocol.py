from abc import ABC, abstractmethod
from src.taxonomy.vision_models_vo import VideoTimeline, FilePath, IntervalSeconds


class VideoTimelineProtocol(ABC):
    """Abstract protocol defining Video Timeline summary capabilities."""

    @abstractmethod
    async def generate_timeline(self, video_path: FilePath, interval: IntervalSeconds) -> VideoTimeline:
        """Generate structured chronological event timeline summarizing a video."""
        pass
