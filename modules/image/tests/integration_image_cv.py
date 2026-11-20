"""Integration tests: image module and DI wiring."""


class TestImageIntegration:
    def test_image_orchestrator_with_processor(self):
        """Verify image orchestrator integrates with image processing processor."""
        from modules.image.src.agent_image_orchestrator import ImageOrchestrator
        from modules.image.src.capabilities_image_processing_processor import (
            ImageProcessingProcessor,
        )
        from modules.shared.src.image.contract_image_aggregate import IImageAggregate

        orch = ImageOrchestrator(ImageProcessingProcessor())
        assert isinstance(orch, IImageAggregate)

    def test_image_orchestrator_execute_returns_output(self):
        """Verify image orchestrator execute_in_process returns a CommandOutput."""
        from modules.image.src.agent_image_orchestrator import ImageOrchestrator
        from modules.image.src.capabilities_image_processing_processor import (
            ImageProcessingProcessor,
        )
        from modules.shared.src.common.taxonomy_vision_vo import (
            CommandName,
            CommandOutput,
            SystemCommandParams,
        )

        orch = ImageOrchestrator(ImageProcessingProcessor())
        result = orch.execute_in_process(
            CommandName(value="analyze"),
            SystemCommandParams(**{"image": "/nonexistent/image.jpg"}),
        )
        assert isinstance(result, CommandOutput)
