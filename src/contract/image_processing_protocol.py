from abc import ABC, abstractmethod
from typing import List
from src.taxonomy import Detection, VisionAnalysis, FilePath, LanguageCode, AnalysisPrompt, OcrText


class ImageProcessingProtocol(ABC):
    """Abstract protocol defining Image Processing capabilities."""

    @abstractmethod
    def analyze_screenshot(self, image_path: FilePath, prompt: AnalysisPrompt) -> VisionAnalysis:
        """Analyze screenshot for UI elements and text descriptions."""
        pass

    @abstractmethod
    def extract_text(self, image_path: FilePath, lang: LanguageCode) -> OcrText:
        """Extract text using OCR capabilities."""
        pass

    @abstractmethod
    def find_elements(self, image_path: FilePath) -> List[Detection]:
        """Locate raw interactive UI elements on the screenshot."""
        pass

    @abstractmethod
    def compare_screenshots(self, image_path1: FilePath, image_path2: FilePath) -> dict:
        """Compare two screenshots to find visual changes."""
        pass
