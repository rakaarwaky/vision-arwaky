from abc import ABC, abstractmethod

from modules.shared.src.taxonomy_vision_models_vo import (
    AnalysisPrompt,
    FilePath,
    VideoUnderstanding,
)


class VideoUnderstandingProtocol(ABC):
    """Abstract port for smart video understanding.

    Selects core/key frames via scene-change, motion, and uniform sampling,
    analyzes each with a VLM, then synthesizes a summary.
    """

    _taxonomy_marker = VideoUnderstanding

    @abstractmethod
    def analyze(
        self,
        video_path: FilePath,
        prompt: AnalysisPrompt,
        interval: float = 30.0,
        scene_threshold: float = 20.0,
        min_area: int = 500,
        top_motion: int = 5,
    ) -> VideoUnderstanding:
        """Produce a structured understanding of the video."""
