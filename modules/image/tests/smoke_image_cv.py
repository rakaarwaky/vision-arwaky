"""Smoke tests: image app boots and responds."""


class TestImageSmoke:
    def test_image_orchestrator_instantiates(self):
        """Verify image orchestrator can be instantiated."""
        from modules.image.src.agent_image_orchestrator import ImageOrchestrator
        from modules.image.src.capabilities_image_processing_processor import (
            ImageProcessingProcessor,
        )

        orch = ImageOrchestrator(ImageProcessingProcessor())
        assert orch is not None

    def test_image_capability_instantiates(self):
        """Verify image processing processor can be instantiated."""
        from modules.image.src.capabilities_image_processing_processor import (
            ImageProcessingProcessor,
        )

        cap = ImageProcessingProcessor()
        assert cap is not None
