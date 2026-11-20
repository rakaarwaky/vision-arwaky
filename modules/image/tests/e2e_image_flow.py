"""E2E tests: full image analysis lifecycle."""


class TestImageE2E:
    def test_image_orchestrator_execute_analyze(self):
        """Verify image orchestrator handles an analyze command end-to-end."""
        from modules.image.src.agent_image_orchestrator import ImageOrchestrator
        from modules.image.src.capabilities_image_processing_processor import (
            ImageProcessingProcessor,
        )
        from modules.shared.src.common.taxonomy_vision_vo import (
            CommandName,
            SystemCommandParams,
        )

        orch = ImageOrchestrator(ImageProcessingProcessor())
        out = orch.execute_in_process(
            CommandName(value="analyze"),
            SystemCommandParams(**{"image": "/nonexistent/image.jpg"}),
        )
        assert out is not None
        assert out.value is not None
