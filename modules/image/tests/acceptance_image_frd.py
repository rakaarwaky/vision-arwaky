"""Acceptance tests: image feature business requirements FR-IMG-001..002."""

from modules.image.src.capabilities_image_processing_processor import (
    ImageProcessingProcessor,
)
from modules.shared.src.common.taxonomy_vision_vo import (
    AnalysisPrompt,
    FilePath,
    VisionAnalysis,
)


class TestImageAcceptance:
    def test_fr_img_001_analyze_image_returns_vision_analysis(self):
        """FR-IMG-001: analyze image returns a structured VisionAnalysis."""
        cap = ImageProcessingProcessor()
        result = cap.analyze_screenshot(
            FilePath(value="/nonexistent/image.jpg"),
            AnalysisPrompt(value="Describe this image."),
        )
        assert isinstance(result, VisionAnalysis)
        assert result.source in ("llm", "opencv")

    def test_fr_img_002_analyze_screenshot_falls_back_without_vlm(self):
        """FR-IMG-002: analyze screenshot falls back when no VLM is configured."""
        cap = ImageProcessingProcessor()
        result = cap.analyze_screenshot(
            FilePath(value="/nonexistent/image.jpg"),
            AnalysisPrompt(value="Describe this image."),
        )
        assert result.source == "opencv"
        assert result.text == "No VLM available"
