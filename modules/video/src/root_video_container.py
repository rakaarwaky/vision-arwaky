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


def build_video_feature(llm_port: LLMVisionProtocol) -> dict[str, Any]:
    """Build and wire all video feature components."""
    ffmpeg = build_ffmpeg()
    video_proc = build_video_processing(ffmpeg)
    video_analysis = build_video_analysis()
    object_tracking = build_object_tracking()
    video_understanding = build_video_understanding(
        video_analysis, video_proc, llm_port
    )
    video_orch = build_video_orchestrator(
        ffmpeg,
        video_proc,
        video_analysis,
        object_tracking,
        video_understanding,
    )

    return {
        "ffmpeg": ffmpeg,
        "video_processing": video_proc,
        "video_analysis": video_analysis,
        "object_tracking": object_tracking,
        "video_understanding": video_understanding,
        "video_orchestrator": video_orch,
    }


