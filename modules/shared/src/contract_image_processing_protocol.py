from abc import ABC, abstractmethod

from modules.shared.src.taxonomy_vision_vo import (
    AnalysisPrompt,
    FilePath,
    LanguageCode,
    OcrText,
    ScreenshotComparison,
    VisionAnalysis,
)


class ImageProcessingProtocol(ABC):
    """Abstract protocol defining Image Processing capabilities."""

    @abstractmethod
    def analyze_screenshot(
        self, image_path: FilePath, prompt: AnalysisPrompt
    ) -> VisionAnalysis:
        """Analyze screenshot for text descriptions and visual content."""

    @abstractmethod
    def extract_text(self, image_path: FilePath, lang: LanguageCode) -> OcrText:
        """Extract text using OCR capabilities."""

    @abstractmethod
    def compare_screenshots(
        self, image_path1: FilePath, image_path2: FilePath
    ) -> ScreenshotComparison:
        """Compare two screenshots to find visual changes."""
