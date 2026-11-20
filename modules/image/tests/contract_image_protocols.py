"""Contract tests: image feature protocol implementations."""

from modules.image.src.agent_image_orchestrator import ImageOrchestrator
from modules.image.src.capabilities_image_processing_processor import (
    ImageProcessingProcessor,
)
from modules.image.src.capabilities_llm_vision_adapter import LLMVisionAdapter
from modules.shared.src.image.contract_image_protocol import (
    IImageProcessingProtocol,
    ILLMVisionProtocol,
)


class TestImageContract:
    def test_image_processing_processor_implements_protocol(self):
        cap = ImageProcessingProcessor()
        assert isinstance(cap, IImageProcessingProtocol)

    def test_llm_vision_adapter_implements_protocol(self):
        adapter = LLMVisionAdapter()
        assert isinstance(adapter, ILLMVisionProtocol)

    def test_image_orchestrator_implements_aggregate(self):
        from modules.shared.src.image.contract_image_aggregate import IImageAggregate

        orch = ImageOrchestrator(ImageProcessingProcessor())
        assert isinstance(orch, IImageAggregate)
