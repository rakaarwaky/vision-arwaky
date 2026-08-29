from abc import ABC, abstractmethod

from modules.shared.src.taxonomy_vision_models_vo import (
    FilePath,
    IntervalSeconds,
    VideoTimeline,
)


class VideoTimelineProtocol(ABC):
    """Abstract protocol defining Video Timeline summary capabilities."""

    @abstractmethod
    async def generate_timeline(
        self, video_path: FilePath, interval: IntervalSeconds
    ) -> VideoTimeline:
        """Generate structured chronological event timeline summarizing a video."""
