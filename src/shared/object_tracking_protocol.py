from abc import ABC, abstractmethod
from typing import List
from src.shared.vision_models_vo import BoundingBox, FilePath, MaxFrames


class ObjectTrackingProtocol(ABC):
    """Abstract protocol defining Object Tracking capabilities."""

    @abstractmethod
    def track_object(
        self,
        video_path: FilePath,
        initial_box: BoundingBox,
        max_frames: MaxFrames,
    ) -> List[BoundingBox]:
        """Track object starting from initial_box throughout the video."""
        pass
