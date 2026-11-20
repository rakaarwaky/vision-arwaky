"""Acceptance tests: video feature business requirements FR-VID-001."""

from unittest.mock import MagicMock, patch

from modules.shared.src.common.taxonomy_vision_vo import (
    AnalysisPrompt,
    BackendType,
    FilePath,
    ModelName,
    VideoUnderstanding,
)
from modules.shared.src.image.contract_image_protocol import ILLMVisionProtocol
from modules.video.src.capabilities_video_understanding import (
    VideoUnderstandingAnalyzer,
)


class _FakeLLM(ILLMVisionProtocol):
    @property
    def backend(self) -> BackendType:
        return BackendType(value="external")

    @property
    def model(self) -> ModelName:
        return ModelName(value="fake-model")

    def analyze_image(self, image_path, prompt, timeout=120):
        return "fake description"


class TestVideoAcceptance:
    def test_fr_vid_001_analyze_returns_understanding(self):
        """FR-VID-001: analyze video returns a structured VideoUnderstanding."""
        fake_meta = {"fps": 30.0, "frame_count": 10, "width": 100, "height": 100}
        fake_cap = MagicMock()
        fake_cap.read.return_value = (False, None)
        fake_cap.set.return_value = None
        fake_cap.release.return_value = None

        with (
            patch(
                "modules.video.src.capabilities_video_understanding.get_video_metadata",
                return_value=fake_meta,
            ),
            patch(
                "modules.video.src.capabilities_video_understanding.check_video_corruption",
                return_value=False,
            ),
            patch(
                "modules.video.src.capabilities_video_understanding.open_video_capture",
                return_value=fake_cap,
            ),
        ):
            analyzer = VideoUnderstandingAnalyzer(llm=_FakeLLM())
            result = analyzer.analyze(
                FilePath(value="dummy.mp4"),
                AnalysisPrompt(value="describe"),
            )
        assert isinstance(result, VideoUnderstanding)
