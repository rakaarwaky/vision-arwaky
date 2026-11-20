"""Contract tests: video feature protocol implementations."""

from modules.shared.src.video.contract_video_protocol import (
    IVideoUnderstandingProtocol,
)
from modules.video.src.agent_video_orchestrator import VideoOrchestrator
from modules.video.src.capabilities_video_understanding import (
    VideoUnderstandingAnalyzer,
)


class TestVideoContract:
    def test_video_understanding_analyzer_implements_protocol(self):
        from modules.shared.src.common.taxonomy_vision_vo import BackendType, ModelName
        from modules.shared.src.image.contract_image_protocol import ILLMVisionProtocol

        class _FakeLLM(ILLMVisionProtocol):
            @property
            def backend(self) -> BackendType:
                return BackendType(value="external")

            @property
            def model(self) -> ModelName:
                return ModelName(value="fake-model")

            def analyze_image(self, image_path, prompt, timeout=120):
                return "fake"

        analyzer = VideoUnderstandingAnalyzer(llm=_FakeLLM())
        assert isinstance(analyzer, IVideoUnderstandingProtocol)

    def test_video_orchestrator_implements_aggregate(self):
        from modules.shared.src.video.contract_video_aggregate import IVideoAggregate

        orch = VideoOrchestrator()
        assert isinstance(orch, IVideoAggregate)
