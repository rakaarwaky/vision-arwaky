"""E2E tests: full video understanding lifecycle."""

from unittest.mock import MagicMock, patch

from modules.shared.src.common.taxonomy_vision_vo import (
    BackendType,
    CommandName,
    ModelName,
    SystemCommandParams,
)
from modules.shared.src.image.contract_image_protocol import ILLMVisionProtocol
from modules.video.src.agent_video_orchestrator import VideoOrchestrator
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


class TestVideoE2E:
    def test_video_orchestrator_execute_analyze_video(self):
        """Verify video orchestrator handles an analyze-video command end-to-end."""
        fake_meta = {"fps": 30.0, "frame_count": 10, "width": 100, "height": 100}
        fake_cap = MagicMock()
        fake_cap.read.return_value = (False, None)
        fake_cap.set.return_value = None
        fake_cap.release.return_value = None

        analyzer = VideoUnderstandingAnalyzer(llm=_FakeLLM())
        orch = VideoOrchestrator(video_understanding=analyzer)

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
            out = orch.execute_in_process(
                CommandName(value="analyze-video"),
                SystemCommandParams(**{"video": "dummy.mp4"}),
            )
        assert out is not None
        assert out.value is not None
