from abc import ABC, abstractmethod
from typing import List
from src.shared.vision_models_vo import SceneChange, MotionEvent, FilePath, SceneThreshold, MinArea


class VideoAnalysisProtocol(ABC):
    """Abstract protocol defining Video Analysis capabilities."""

    @abstractmethod
    def detect_scenes(self, video_path: FilePath, threshold: SceneThreshold) -> List[SceneChange]:
        """Detect scene transitions / transitions in video content."""
        pass

    @abstractmethod
    def detect_motion(self, video_path: FilePath, min_area: MinArea) -> List[MotionEvent]:
        """Detect significant frame-to-frame motion events."""
        pass
