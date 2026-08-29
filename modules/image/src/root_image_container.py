"""Image Feature Composition Root Container.

Wires image capabilities and adapters to contract interfaces.
"""

from typing import Any

from modules.image.src.agent_image_orchestrator import ImageOrchestrator
from modules.image.src.capabilities_image_processing_processor import (
    ImageProcessingProcessor,
)
from modules.image.src.capabilities_llm_vision_adapter import LLMVisionAdapter
from modules.image.src.capabilities_tesseract_ocr_adapter import TesseractOCRAdapter


def build_tesseract() -> TesseractOCRAdapter:
    """Instantiate Tesseract OCR adapter."""
    return TesseractOCRAdapter()


def build_llm() -> LLMVisionAdapter:
    """Instantiate LLM vision adapter."""
    return LLMVisionAdapter()


def build_image_processing(
    tesseract_port: TesseractOCRAdapter,
    llm_port: LLMVisionAdapter,
) -> ImageProcessingProcessor:
    """Wire ImageProcessingProcessor capability."""
    return ImageProcessingProcessor(
        tesseract_port=tesseract_port,
        llm_port=llm_port,
    )


def build_image_orchestrator(
    tesseract_port: TesseractOCRAdapter,
    llm_port: LLMVisionAdapter,
    image_processing_port: ImageProcessingProcessor,
) -> ImageOrchestrator:
    """Instantiate Image Agent Orchestrator with injected ports."""
    return ImageOrchestrator(
        image_processing=image_processing_port,
        tesseract=tesseract_port,
        llm=llm_port,
    )


def build_image_feature() -> dict[str, Any]:
    """Build and wire all image feature components."""
    tesseract = build_tesseract()
    llm = build_llm()
    image_proc = build_image_processing(tesseract, llm)
    image_orch = build_image_orchestrator(tesseract, llm, image_proc)

    return {
        "tesseract": tesseract,
        "llm": llm,
        "image_processing": image_proc,
        "image_orchestrator": image_orch,
    }

