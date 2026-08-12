"""Root Container — Composition root for dependency injection.

Wires all infrastructure adapters and capabilities together,
then exposes them to CLI/MCP/TUI surface layers.
Mirrors lint-arwaky's CommonDeps::build() pattern.
"""

import importlib
from typing import Any


# ─── Infrastructure Adapters ────────────────────────────────────────────────


def _load_module(module_path: str, class_name: str) -> type:
    """Dynamically load a module and return the class by name."""
    mod = importlib.import_module(module_path)
    return getattr(mod, class_name)


def build_opencv() -> Any:
    """Instantiate OpenCV image adapter."""
    cls = _load_module(
        "src.opencv.infrastructure_opencv_image_adapter", "OpenCVImageAdapter"
    )
    return cls()


def build_tesseract() -> Any:
    """Instantiate Tesseract OCR adapter."""
    cls = _load_module(
        "src.image.infrastructure_tesseract_ocr_adapter", "TesseractOCRAdapter"
    )
    return cls()


def build_llm() -> Any:
    """Instantiate LLM Vision adapter."""
    cls = _load_module(
        "src.image.infrastructure_llm_vision_adapter", "LLMVisionAdapter"
    )
    return cls()


def build_ffmpeg() -> Any:
    """Instantiate FFmpeg video adapter."""
    cls = _load_module(
        "src.video.infrastructure_ffmpeg_video_adapter", "FFmpegVideoAdapter"
    )
    return cls()


def build_utils() -> Any:
    """Instantiate System Utils adapter."""
    cls = _load_module(
        "src.system_utils.infrastructure_system_utils_util", "SystemUtilsUtil"
    )
    return cls()


# ─── Capabilities ──────────────────────────────────────────────────────────


def build_image_processing(opencv: Any, tesseract: Any, llm: Any) -> Any:
    """Instantiate ImageProcessingProcessor with injected ports."""
    cls = _load_module(
        "src.image.capabilities_image_processing_processor", "ImageProcessingProcessor"
    )
    return cls(opencv_port=opencv, tesseract_port=tesseract, llm_port=llm)


def build_video_processing(opencv: Any, ffmpeg: Any) -> Any:
    """Instantiate VideoProcessingProcessor with injected ports."""
    cls = _load_module(
        "src.video.capabilities_video_processing_processor", "VideoProcessingProcessor"
    )
    return cls(opencv_port=opencv, ffmpeg_port=ffmpeg)


def build_video_analysis(opencv: Any) -> Any:
    """Instantiate VideoAnalysisAnalyzer with injected ports."""
    cls = _load_module(
        "src.video.capabilities_video_analysis_analyzer", "VideoAnalysisAnalyzer"
    )
    return cls(opencv_port=opencv)


def build_video_timeline(opencv: Any, video_proc: Any, analysis: Any) -> Any:
    """Instantiate VideoTimelineGenerator with injected ports."""
    cls = _load_module(
        "src.video.capabilities_video_timeline_generator", "VideoTimelineGenerator"
    )
    return cls(opencv_port=opencv, video_cap=video_proc, analysis_cap=analysis)


def build_object_tracking(opencv: Any) -> Any:
    """Instantiate ObjectTrackingTracker with injected ports."""
    cls = _load_module(
        "src.tracking.capabilities_object_tracking_tracker", "ObjectTrackingTracker"
    )
    return cls(opencv_port=opencv)


def build_visual_memory(opencv: Any, utils: Any) -> Any:
    """Instantiate VisualMemoryStore with injected ports."""
    cls = _load_module(
        "src.memory.capabilities_visual_memory_repository", "VisualMemoryStore"
    )
    return cls(opencv_port=opencv, utils_port=utils)


# ─── Composition Root ──────────────────────────────────────────────────────


def build() -> dict[str, Any]:
    """Build all dependencies and wire them together.

    Returns a dict keyed by capability/adapters — the dependency container
    that surface layers (MCP, CLI, TUI) consume.
    """
    # Infrastructure first
    opencv = build_opencv()
    tesseract = build_tesseract()
    llm = build_llm()
    ffmpeg = build_ffmpeg()
    utils = build_utils()

    # Capabilities (inject infrastructure)
    image_proc = build_image_processing(opencv, tesseract, llm)
    video_proc = build_video_processing(opencv, ffmpeg)
    video_analysis = build_video_analysis(opencv)
    video_timeline = build_video_timeline(opencv, video_proc, video_analysis)
    obj_tracking = build_object_tracking(opencv)
    visual_mem = build_visual_memory(opencv, utils)

    return {
        # Infrastructure adapters
        "opencv": opencv,
        "tesseract": tesseract,
        "llm": llm,
        "ffmpeg": ffmpeg,
        "utils": utils,
        # Capabilities
        "image_processing": image_proc,
        "video_processing": video_proc,
        "video_analysis": video_analysis,
        "video_timeline": video_timeline,
        "object_tracking": obj_tracking,
        "visual_memory": visual_mem,
    }
