from typing import Any

from modules.shared.src.contract_llm_vision_protocol import LLMVisionProtocol
from modules.video.src.agent_video_orchestrator import VideoOrchestrator
from modules.video.src.capabilities_ffmpeg_adapter import FFmpegVideoAdapter
from modules.video.src.capabilities_object_tracker import ObjectTrackingTracker
from modules.video.src.capabilities_video_analyzer import VideoAnalysisAnalyzer
from modules.video.src.capabilities_video_processor import VideoProcessingProcessor
from modules.video.src.capabilities_video_understanding import (
    VideoUnderstandingAnalyzer,
)


def build_ffmpeg() -> FFmpegVideoAdapter:
    """Instantiate FFmpeg video adapter."""
    return FFmpegVideoAdapter()


def build_video_processing(
    ffmpeg_port: FFmpegVideoAdapter,
) -> VideoProcessingProcessor:
    """Wire VideoProcessingProcessor capability."""
    return VideoProcessingProcessor(ffmpeg_port=ffmpeg_port)


def build_video_analysis() -> VideoAnalysisAnalyzer:
    """Wire VideoAnalysisAnalyzer capability."""
    return VideoAnalysisAnalyzer()


def build_object_tracking() -> ObjectTrackingTracker:
    """Wire ObjectTrackingTracker capability."""
    return ObjectTrackingTracker()


def build_video_understanding(
    video_analysis: VideoAnalysisAnalyzer,
    video_proc: VideoProcessingProcessor,
    llm_port: LLMVisionProtocol,
) -> VideoUnderstandingAnalyzer:
    """Wire VideoUnderstandingAnalyzer capability (smart video understanding)."""
    return VideoUnderstandingAnalyzer(
        video_analysis=video_analysis,
        video_processing=video_proc,
        llm=llm_port,
    )


def build_video_orchestrator(
    ffmpeg_port: FFmpegVideoAdapter,
    video_proc: VideoProcessingProcessor,
    video_analysis: VideoAnalysisAnalyzer,
    object_tracking: ObjectTrackingTracker,
    video_understanding: VideoUnderstandingAnalyzer,
) -> VideoOrchestrator:
    """Instantiate Video Agent Orchestrator with injected ports."""
    return VideoOrchestrator(
        video_processing=video_proc,
        video_analysis=video_analysis,
        object_tracking=object_tracking,
        ffmpeg=ffmpeg_port,
        video_understanding=video_understanding,
    )


class VideoContainer:
    """Composition root for the video domain."""

    def __init__(
        self,
        llm_port: LLMVisionProtocol | None = None,
        ffmpeg_port: FFmpegVideoAdapter | None = None,
        video_processing_port: VideoProcessingProcessor | None = None,
        video_analysis_port: VideoAnalysisAnalyzer | None = None,
        object_tracking_port: ObjectTrackingTracker | None = None,
        video_understanding_port: VideoUnderstandingAnalyzer | None = None,
        orchestrator: VideoOrchestrator | None = None,
    ) -> None:
        self._ffmpeg = ffmpeg_port or build_ffmpeg()
        self._video_processing = video_processing_port or build_video_processing(
            self._ffmpeg
        )
        self._video_analysis = video_analysis_port or build_video_analysis()
        self._object_tracking = object_tracking_port or build_object_tracking()

        if video_understanding_port is not None:
            self._video_understanding = video_understanding_port
        else:
            if llm_port is None:
                from modules.image.src.root_image_container import ImageContainer

                llm_port = ImageContainer().llm
            self._video_understanding = build_video_understanding(
                self._video_analysis, self._video_processing, llm_port
            )

        self._orchestrator = orchestrator or build_video_orchestrator(
            self._ffmpeg,
            self._video_processing,
            self._video_analysis,
            self._object_tracking,
            self._video_understanding,
        )

    @property
    def orchestrator(self) -> VideoOrchestrator:
        """Return the wired Video Agent Orchestrator."""
        return self._orchestrator

    @property
    def ffmpeg(self) -> FFmpegVideoAdapter:
        """Return the FFmpeg video adapter."""
        return self._ffmpeg

    @property
    def video_processing(self) -> VideoProcessingProcessor:
        """Return the VideoProcessingProcessor capability."""
        return self._video_processing

    @property
    def video_analysis(self) -> VideoAnalysisAnalyzer:
        """Return the VideoAnalysisAnalyzer capability."""
        return self._video_analysis

    @property
    def object_tracking(self) -> ObjectTrackingTracker:
        """Return the ObjectTrackingTracker capability."""
        return self._object_tracking

    @property
    def video_understanding(self) -> VideoUnderstandingAnalyzer:
        """Return the VideoUnderstandingAnalyzer capability."""
        return self._video_understanding


def build_video_feature(
    llm_port: LLMVisionProtocol | None = None,
) -> dict[str, Any]:
    """Build and wire all video feature components."""
    container = VideoContainer(llm_port=llm_port)
    return {
        "ffmpeg": container.ffmpeg,
        "video_processing": container.video_processing,
        "video_analysis": container.video_analysis,
        "object_tracking": container.object_tracking,
        "video_understanding": container.video_understanding,
        "video_orchestrator": container.orchestrator,
        "container": container,
    }


__all__ = [
    "VideoContainer",
    "build_ffmpeg",
    "build_object_tracking",
    "build_video_analysis",
    "build_video_feature",
    "build_video_orchestrator",
    "build_video_processing",
    "build_video_understanding",
]
