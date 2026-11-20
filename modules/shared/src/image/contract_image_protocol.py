"""Image-domain capability contracts (AES102 `_protocol`).

One file for the image feature. Each class below is one capability
seam: a class carries every method that capability implements, with one
concrete return type each, so a capability implements its class outright
and never carries stubs.
"""

from abc import ABC, abstractmethod

from modules.shared.src.common.taxonomy_vision_constant import DEFAULT_VLM_TIMEOUT_S
from modules.shared.src.common.taxonomy_vision_vo import (
    AnalysisPrompt,
    BackendType,
    FilePath,
    ModelName,
    VisionAnalysis,
)


class IImageProcessingProtocol(ABC):
    """Image processing capability: screenshot and image analysis."""

    @abstractmethod
    def analyze_screenshot(
        self, image_path: FilePath, prompt: AnalysisPrompt
    ) -> VisionAnalysis:
        """Analyze screenshot for visual content. Return structured analysis."""
        ...


class ILLMVisionProtocol(ABC):
    """VLM backend capability: local/external image analysis."""

    @property
    @abstractmethod
    def backend(self) -> BackendType:
        """The active backend type: external."""
        ...

    @property
    @abstractmethod
    def model(self) -> ModelName:
        """The active model name."""
        ...

    @abstractmethod
    def analyze_image(
        self,
        image_path: FilePath,
        prompt: AnalysisPrompt,
        timeout: int = DEFAULT_VLM_TIMEOUT_S,
    ) -> str:
        """Analyze image with custom prompt using the VLM. Return analysis text."""
        ...


__all__ = ["IImageProcessingProtocol", "ILLMVisionProtocol"]

_layer_symbols = {
    "IImageProcessingProtocol": IImageProcessingProtocol,
    "ILLMVisionProtocol": ILLMVisionProtocol,
}
