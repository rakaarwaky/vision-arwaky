from abc import ABC, abstractmethod

from modules.shared.src.taxonomy_vision_models_vo import (
    AnalysisPrompt,
    BackendType,
    FilePath,
    ModelName,
)


class LLMVisionProtocol(ABC):
    """Abstract port for local VLM image analysis capabilities."""

    @property
    @abstractmethod
    def backend(self) -> BackendType:
        """The active backend type: external."""

    @property
    @abstractmethod
    def model(self) -> ModelName:
        """The active model name."""

    @abstractmethod
    def analyze_image(
        self,
        image_path: FilePath,
        prompt: AnalysisPrompt,
        timeout: int = 120,
    ) -> str:
        """Analyze image with custom prompt using the VLM."""

    @abstractmethod
    def analyze_video(
        self,
        video_path: FilePath,
        prompt: AnalysisPrompt,
        timeout: int = 300,
    ) -> str:
        """Analyze video with custom prompt using the VLM (video understanding)."""
