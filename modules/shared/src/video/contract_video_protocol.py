"""Video-domain capability contracts (AES102 `_protocol`).

One file for the video feature. Each class below is one capability
seam: a class carries every method that capability implements, with one
concrete return type each, so a capability implements its class outright
and never carries stubs.
"""

from abc import ABC, abstractmethod

from modules.shared.src.common.taxonomy_vision_vo import (
    AnalysisPrompt,
    FilePath,
    VideoUnderstanding,
    VideoUnderstandingConfig,
)


class IVideoUnderstandingProtocol(ABC):
    """Video understanding capability: smart frame sampling, VLM analysis, summary."""

    @abstractmethod
    def analyze(
        self,
        video_path: FilePath,
        prompt: AnalysisPrompt,
        config: VideoUnderstandingConfig | None = None,
    ) -> VideoUnderstanding:
        """Produce a structured understanding of the video."""
        ...


__all__ = ["IVideoUnderstandingProtocol"]

_layer_symbols = {"IVideoUnderstandingProtocol": IVideoUnderstandingProtocol}
