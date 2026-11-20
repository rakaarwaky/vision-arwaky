from typing import Any

from modules.shared.src.image.contract_image_protocol import ILLMVisionProtocol
from modules.shared.src.video.contract_video_aggregate import IVideoAggregate
from modules.video.src.agent_video_orchestrator import VideoOrchestrator
from modules.video.src.capabilities_video_understanding import (
    VideoUnderstandingAnalyzer,
)


def build_video_orchestrator(
    video_understanding: VideoUnderstandingAnalyzer | None = None,
) -> VideoOrchestrator:
    """Instantiate Video Agent Orchestrator with injected ports."""
    return VideoOrchestrator(
        video_understanding=video_understanding,
    )


class VideoContainer:
    """Composition root for the video domain."""

    def __init__(
        self,
        llm_port: ILLMVisionProtocol | None = None,
        video_understanding_port: VideoUnderstandingAnalyzer | None = None,
        orchestrator: VideoOrchestrator | None = None,
    ) -> None:
        self._video_understanding: VideoUnderstandingAnalyzer | None
        if video_understanding_port is not None:
            self._video_understanding = video_understanding_port
        elif llm_port is not None:
            self._video_understanding = VideoUnderstandingAnalyzer(
                llm=llm_port,
            )
        else:
            self._video_understanding = None

        self._orchestrator = orchestrator or build_video_orchestrator(
            self._video_understanding,
        )

    @property
    def orchestrator(self) -> IVideoAggregate:
        """Return the wired Video Agent Orchestrator (as its aggregate seam)."""
        return self._orchestrator

    @property
    def video_understanding(self) -> VideoUnderstandingAnalyzer | None:
        """Return the VideoUnderstandingAnalyzer capability."""
        return self._video_understanding


def build_video_feature(
    llm_port: ILLMVisionProtocol | None = None,
) -> dict[str, Any]:
    """Build and wire all video feature components."""
    container = VideoContainer(llm_port=llm_port)
    return {
        "video_understanding": container.video_understanding,
        "video_orchestrator": container.orchestrator,
        "container": container,
    }


__all__ = [
    "VideoContainer",
    "build_video_feature",
    "build_video_orchestrator",
]
