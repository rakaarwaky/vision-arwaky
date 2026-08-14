"""Video Feature Composition Root Container.

Wires video capabilities and adapters to contract interfaces.
"""

from typing import Any

from modules.opencv.src.capabilities_opencv_image_adapter import OpenCVImageAdapter
from modules.shared.src.contract_llm_vision_protocol import LLMVisionProtocol
from modules.video.src.agent_video_orchestrator import VideoOrchestrator
from modules.video.src.capabilities_ffmpeg_adapter import FFmpegVideoAdapter
from modules.video.src.capabilities_object_tracker import ObjectTrackingTracker
from modules.video.src.capabilities_timeline_generator import VideoTimelineGenerator
from modules.video.src.capabilities_video_analyzer import VideoAnalysisAnalyzer
from modules.video.src.capabilities_video_processor import VideoProcessingProcessor
from modules.video.src.capabilities_video_understanding import (
    VideoUnderstandingAnalyzer,
)


def build_ffmpeg() -> FFmpegVideoAdapter:
    """Instantiate FFmpeg video adapter."""
    return FFmpegVideoAdapter()


def build_video_processing(
    opencv_port: OpenCVImageAdapter, ffmpeg_port: FFmpegVideoAdapter
) -> VideoProcessingProcessor:
    """Wire VideoProcessingProcessor capability."""
    return VideoProcessingProcessor(opencv_port=opencv_port, ffmpeg_port=ffmpeg_port)


def build_video_analysis(opencv_port: OpenCVImageAdapter) -> VideoAnalysisAnalyzer:
    """Wire VideoAnalysisAnalyzer capability."""
    return VideoAnalysisAnalyzer(opencv_port=opencv_port)


def build_video_timeline(
    opencv_port: OpenCVImageAdapter,
    video_proc: VideoProcessingProcessor,
    analysis_cap: VideoAnalysisAnalyzer,
) -> VideoTimelineGenerator:
    """Wire VideoTimelineGenerator capability."""
    return VideoTimelineGenerator(
        opencv_port=opencv_port, video_cap=video_proc, analysis_cap=analysis_cap
    )


def build_object_tracking(opencv_port: OpenCVImageAdapter) -> ObjectTrackingTracker:
    """Wire ObjectTrackingTracker capability."""
    return ObjectTrackingTracker(opencv_port=opencv_port)


def build_video_understanding(
    video_analysis: VideoAnalysisAnalyzer,
    video_proc: VideoProcessingProcessor,
    llm_port: LLMVisionProtocol,
    opencv_port: OpenCVImageAdapter,
) -> VideoUnderstandingAnalyzer:
    """Wire VideoUnderstandingAnalyzer capability (smart video understanding)."""
    return VideoUnderstandingAnalyzer(
        video_analysis=video_analysis,
        video_processing=video_proc,
        llm=llm_port,
        opencv=opencv_port,
    )


def build_video_orchestrator(
    opencv_port: OpenCVImageAdapter,
    ffmpeg_port: FFmpegVideoAdapter,
    video_proc: VideoProcessingProcessor,
    video_analysis: VideoAnalysisAnalyzer,
    video_timeline: VideoTimelineGenerator,
    object_tracking: ObjectTrackingTracker,
    video_understanding: VideoUnderstandingAnalyzer,
) -> VideoOrchestrator:
    """Instantiate Video Agent Orchestrator with injected ports."""
    return VideoOrchestrator(
        video_processing=video_proc,
        video_analysis=video_analysis,
        video_timeline=video_timeline,
        object_tracking=object_tracking,
        opencv=opencv_port,
        ffmpeg=ffmpeg_port,
        video_understanding=video_understanding,
    )


def build_video_feature(
    opencv_port: OpenCVImageAdapter, llm_port: LLMVisionProtocol
) -> dict[str, Any]:
    """Build and wire all video feature components."""
    ffmpeg = build_ffmpeg()
    video_proc = build_video_processing(opencv_port, ffmpeg)
    video_analysis = build_video_analysis(opencv_port)
    video_timeline = build_video_timeline(opencv_port, video_proc, video_analysis)
    object_tracking = build_object_tracking(opencv_port)
    video_understanding = build_video_understanding(
        video_analysis, video_proc, llm_port, opencv_port
    )
    video_orch = build_video_orchestrator(
        opencv_port,
        ffmpeg,
        video_proc,
        video_analysis,
        video_timeline,
        object_tracking,
        video_understanding,
    )

    return {
        "ffmpeg": ffmpeg,
        "video_processing": video_proc,
        "video_analysis": video_analysis,
        "video_timeline": video_timeline,
        "object_tracking": object_tracking,
        "video_understanding": video_understanding,
        "video_orchestrator": video_orch,
    }
