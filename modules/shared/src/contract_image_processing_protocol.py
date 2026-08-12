from abc import ABC, abstractmethod

from modules.shared.src.taxonomy_vision_models_vo import (
    AnalysisPrompt,
    CommandOutput,
    Detection,
    FilePath,
    LanguageCode,
    OcrText,
    VisionAnalysis,
)


class ImageProcessingProtocol(ABC):
    """Abstract protocol defining Image Processing capabilities."""

    @abstractmethod
    def analyze_screenshot(self, image_path: FilePath, prompt: AnalysisPrompt) -> VisionAnalysis:
        """Analyze screenshot for UI elements and text descriptions."""

    @abstractmethod
    def extract_text(self, image_path: FilePath, lang: LanguageCode) -> OcrText:
        """Extract text using OCR capabilities."""

    @abstractmethod
    def find_elements(self, image_path: FilePath) -> list[Detection]:
        """Locate raw interactive UI elements on the screenshot."""

    @abstractmethod
    def compare_screenshots(self, image_path1: FilePath, image_path2: FilePath) -> CommandOutput:
        """Compare two screenshots to find visual changes."""
