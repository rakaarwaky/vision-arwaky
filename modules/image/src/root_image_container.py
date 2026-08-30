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
    image_processing_port: ImageProcessingProcessor,
) -> ImageOrchestrator:
    """Instantiate Image Agent Orchestrator with the single routing port."""
    return ImageOrchestrator(image_processing=image_processing_port)


class ImageContainer:
    """Composition root for the image domain."""

    def __init__(
        self,
        tesseract_port: TesseractOCRAdapter | None = None,
        llm_port: LLMVisionAdapter | None = None,
        image_processing_port: ImageProcessingProcessor | None = None,
        orchestrator: ImageOrchestrator | None = None,
    ) -> None:
        self._tesseract = tesseract_port or build_tesseract()
        self._llm = llm_port or build_llm()
        self._image_processing = image_processing_port or build_image_processing(
            self._tesseract, self._llm
        )
        self._orchestrator = orchestrator or build_image_orchestrator(
            self._image_processing
        )

    @property
    def orchestrator(self) -> ImageOrchestrator:
        """Return the wired Image Agent Orchestrator."""
        return self._orchestrator

    @property
    def tesseract(self) -> TesseractOCRAdapter:
        """Return the Tesseract OCR adapter."""
        return self._tesseract

    @property
    def llm(self) -> LLMVisionAdapter:
        """Return the LLM vision adapter."""
        return self._llm

    @property
    def image_processing(self) -> ImageProcessingProcessor:
        """Return the ImageProcessingProcessor capability."""
        return self._image_processing


def build_image_feature() -> dict[str, Any]:
    """Build and wire all image feature components."""
    container = ImageContainer()
    return {
        "tesseract": container.tesseract,
        "llm": container.llm,
        "image_processing": container.image_processing,
        "image_orchestrator": container.orchestrator,
        "container": container,
    }


__all__ = [
    "ImageContainer",
    "build_image_feature",
    "build_image_orchestrator",
    "build_image_processing",
    "build_llm",
    "build_tesseract",
]
