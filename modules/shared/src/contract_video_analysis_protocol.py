from abc import ABC, abstractmethod

from modules.shared.src.taxonomy_vision_models_vo import (
    FilePath,
    MinArea,
    MotionEvent,
    SceneChange,
    SceneThreshold,
)


class VideoAnalysisProtocol(ABC):
    """Abstract protocol defining Video Analysis capabilities."""

    @abstractmethod
    def detect_scenes(self, video_path: FilePath, threshold: SceneThreshold) -> list[SceneChange]:
        """Detect scene transitions / transitions in video content."""

    @abstractmethod
    def detect_motion(self, video_path: FilePath, min_area: MinArea) -> list[MotionEvent]:
        """Detect significant frame-to-frame motion events."""
