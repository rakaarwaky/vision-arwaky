"""Contract tests: image feature implements shared protocols and aggregate."""

import inspect

from modules.image.src.agent_image_orchestrator import ImageOrchestrator
from modules.image.src.capabilities_image_processing_processor import (
    ImageProcessingProcessor,
)
from modules.image.src.capabilities_llm_vision_adapter import LLMVisionAdapter
from modules.image.src.capabilities_tesseract_ocr_adapter import TesseractOCRAdapter
from modules.shared.src.contract_image_processing_protocol import (
    IImageProcessingProtocol,
)
from modules.shared.src.contract_registry_service_aggregate import (
    IRegistryServiceAggregate,
)
from modules.shared.src.contract_tesseract_ocr_protocol import (
    ITesseractOCRProtocol,
)


class TestImageContracts:
    def test_processor_implements_protocol(self):
        assert inspect.isclass(ImageProcessingProcessor)
        assert issubclass(ImageProcessingProcessor, IImageProcessingProtocol)

    def test_tesseract_adapter_implements_protocol(self):
        assert issubclass(TesseractOCRAdapter, ITesseractOCRProtocol)

    def test_orchestrator_implements_aggregate(self):
        assert issubclass(ImageOrchestrator, IRegistryServiceAggregate)

    def test_processor_public_methods_present(self):
        methods = {
            name
            for name, _ in inspect.getmembers(
                ImageProcessingProcessor, inspect.isfunction
            )
            if not name.startswith("_")
        }
        assert "analyze_screenshot" in methods
        assert "extract_text" in methods
        assert "compare_screenshots" in methods

    def test_protocol_abstract_methods_respected(self):
        abstract = set(getattr(IImageProcessingProtocol, "__abstractmethods__", set()))
        assert "analyze_screenshot" in abstract
        assert "extract_text" in abstract
        assert "compare_screenshots" in abstract

    def test_llm_adapter_instantiable(self):
        assert isinstance(LLMVisionAdapter(), object)
