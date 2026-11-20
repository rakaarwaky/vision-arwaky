"""Smoke tests: video app boots and responds."""


class TestVideoSmoke:
    def test_video_orchestrator_instantiates(self):
        """Verify video orchestrator can be instantiated."""
        from modules.video.src.agent_video_orchestrator import VideoOrchestrator

        orch = VideoOrchestrator()
        assert orch is not None

    def test_video_analyzer_instantiates(self):
        """Verify video understanding analyzer can be instantiated."""
        from modules.shared.src.common.taxonomy_vision_vo import BackendType, ModelName
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
                return "fake"

        analyzer = VideoUnderstandingAnalyzer(llm=_FakeLLM())
        assert analyzer is not None
