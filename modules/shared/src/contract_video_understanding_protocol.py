from abc import ABC, abstractmethod

from modules.shared.src.taxonomy_vision_vo import (
    AnalysisPrompt,
    FilePath,
    VideoUnderstanding,
    VideoUnderstandingConfig,
)


class VideoUnderstandingProtocol(ABC):
    """Abstract port for smart video understanding.

    Selects core/key frames via scene-change, motion, and uniform sampling,
    analyzes each with a VLM, then synthesizes a summary.
    """

    @abstractmethod
    def analyze(
        self,
        video_path: FilePath,
        prompt: AnalysisPrompt,
        config: VideoUnderstandingConfig | None = None,
    ) -> VideoUnderstanding:
        """Produce a structured understanding of the video."""
