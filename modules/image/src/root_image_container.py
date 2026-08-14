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
from modules.opencv.src.capabilities_opencv_image_adapter import OpenCVImageAdapter


def build_tesseract() -> TesseractOCRAdapter:
    """Instantiate Tesseract OCR adapter."""
    return TesseractOCRAdapter()


def build_llm() -> LLMVisionAdapter:
    """Instantiate LLM vision adapter."""
    return LLMVisionAdapter()


def build_image_processing(
    opencv_port: OpenCVImageAdapter,
    tesseract_port: TesseractOCRAdapter,
    llm_port: LLMVisionAdapter,
) -> ImageProcessingProcessor:
    """Wire ImageProcessingProcessor capability."""
    return ImageProcessingProcessor(
        opencv_port=opencv_port,
        tesseract_port=tesseract_port,
        llm_port=llm_port,
    )


def build_image_orchestrator(
    opencv_port: OpenCVImageAdapter,
    tesseract_port: TesseractOCRAdapter,
    llm_port: LLMVisionAdapter,
    image_processing_port: ImageProcessingProcessor,
) -> ImageOrchestrator:
    """Instantiate Image Agent Orchestrator with injected ports."""
    return ImageOrchestrator(
        image_processing=image_processing_port,
        opencv=opencv_port,
        tesseract=tesseract_port,
        llm=llm_port,
    )


def build_image_feature(opencv_port: OpenCVImageAdapter) -> dict[str, Any]:
    """Build and wire all image feature components."""
    tesseract = build_tesseract()
    llm = build_llm()
    image_proc = build_image_processing(opencv_port, tesseract, llm)
    image_orch = build_image_orchestrator(opencv_port, tesseract, llm, image_proc)

    return {
        "tesseract": tesseract,
        "llm": llm,
        "image_processing": image_proc,
        "image_orchestrator": image_orch,
    }
