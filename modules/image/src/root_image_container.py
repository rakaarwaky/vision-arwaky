"""Image Feature Composition Root Container.

Wires image capabilities and adapters to contract interfaces.
"""

from typing import Any

from modules.image.src.agent_image_orchestrator import ImageOrchestrator
from modules.image.src.capabilities_image_processing_processor import (
    ImageProcessingProcessor,
)
from modules.image.src.capabilities_llm_vision_adapter import LLMVisionAdapter
from modules.shared.src.image.contract_image_aggregate import IImageAggregate


def build_llm() -> LLMVisionAdapter:
    """Instantiate LLM vision adapter."""
    return LLMVisionAdapter()


def build_image_processing(
    llm_port: LLMVisionAdapter,
) -> ImageProcessingProcessor:
    """Wire ImageProcessingProcessor capability."""
    return ImageProcessingProcessor(
        llm_port=llm_port,
    )


def build_image_orchestrator(
    image_processing_port: ImageProcessingProcessor,
) -> ImageOrchestrator:
    """Instantiate Image Agent Orchestrator."""
    return ImageOrchestrator(
        image_processing=image_processing_port,
    )


class ImageContainer:
    """Composition root for the image domain."""

    def __init__(
        self,
        llm_port: LLMVisionAdapter | None = None,
        image_processing_port: ImageProcessingProcessor | None = None,
        orchestrator: ImageOrchestrator | None = None,
    ) -> None:
        self._llm = llm_port or build_llm()
        self._image_processing = image_processing_port or build_image_processing(
            self._llm
        )
        self._orchestrator = orchestrator or build_image_orchestrator(
            self._image_processing,
        )

    @property
    def orchestrator(self) -> IImageAggregate:
        """Return the wired Image Agent Orchestrator (as its aggregate seam)."""
        return self._orchestrator

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
]
