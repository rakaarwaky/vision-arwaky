from abc import ABC, abstractmethod

from modules.shared.src.taxonomy_vision_vo import (
    AnalysisPrompt,
    FilePath,
    VisionAnalysis,
)


class IImageProcessingProtocol(ABC):
    """Abstract protocol defining image analysis capabilities."""

    @abstractmethod
    def analyze_screenshot(
        self, image_path: FilePath, prompt: AnalysisPrompt
    ) -> VisionAnalysis:
        """Analyze screenshot for visual content."""
