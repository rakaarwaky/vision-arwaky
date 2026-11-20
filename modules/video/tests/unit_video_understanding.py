"""Unit tests for VideoUnderstandingAnalyzer."""

from unittest.mock import MagicMock, patch

from modules.shared.src.common.taxonomy_vision_constant import MAX_SMART_VIDEO_FRAMES
from modules.shared.src.common.taxonomy_vision_vo import (
    AnalysisPrompt,
    BackendType,
    FilePath,
    ModelName,
    VideoUnderstandingConfig,
)
from modules.shared.src.image.contract_llm_vision_protocol import ILLMVisionProtocol
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


class TestVideoUnderstandingAnalyzer:
    def test_select_frame_indices_bounded(self):
        analyzer = VideoUnderstandingAnalyzer(llm=_FakeLLM())
        indices, step = analyzer._select_frame_indices(
            FilePath(value="dummy.mp4"),
            fps=30.0,
            frame_count=1000,
            config=VideoUnderstandingConfig(interval=1.0),
        )
        assert len(indices) <= MAX_SMART_VIDEO_FRAMES
        assert step == 1.0

    def test_synthesize_summary_empty_descriptions(self):
        analyzer = VideoUnderstandingAnalyzer(llm=_FakeLLM())
        result = analyzer.synthesize_summary([], [])
        assert result == "No frames could be extracted for analysis."

    def test_synthesize_summary_truncates_long_input(self):
        from modules.shared.src.common.taxonomy_vision_constant import (
            MAX_SUMMARY_PROMPT_CHARS,
        )

        analyzer = VideoUnderstandingAnalyzer(llm=_FakeLLM())
        long_desc = "x" * (MAX_SUMMARY_PROMPT_CHARS + 500)
        result = analyzer.synthesize_summary([], [long_desc])
        assert len(result) <= MAX_SUMMARY_PROMPT_CHARS + 80

    def test_analyze_with_corrupted_video(self):
        analyzer = VideoUnderstandingAnalyzer(llm=_FakeLLM())
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
                return_value=True,
            ),
            patch(
                "modules.video.src.capabilities_video_understanding.open_video_capture",
                return_value=fake_cap,
            ),
        ):
            result = analyzer.analyze(
                FilePath(value="dummy.mp4"),
                AnalysisPrompt(value="describe"),
            )
            assert result.video["corrupted"] is True
            assert result.sampling["scene_changes"] == 0
            assert result.sampling["motion_events"] == 0
