"""Root Composition Container — Composition root for dependency injection.

Wires all infrastructure adapters and capabilities together,
then exposes them to CLI/MCP/TUI surface layers.
"""

import importlib
from typing import Any


def _load_module(module_path: str, class_name: str) -> type:
    mod = importlib.import_module(module_path)
    return getattr(mod, class_name)


def build_opencv() -> Any:
    cls = _load_module(
        "modules.opencv.src.infrastructure_opencv_image_adapter", "OpenCVImageAdapter"
    )
    return cls()


def build_tesseract() -> Any:
    cls = _load_module(
        "modules.image.src.infrastructure_tesseract_ocr_adapter", "TesseractOCRAdapter"
    )
    return cls()


def build_llm() -> Any:
    cls = _load_module(
        "modules.image.src.infrastructure_llm_vision_adapter", "LLMVisionAdapter"
    )
    return cls()


def build_ffmpeg() -> Any:
    cls = _load_module(
        "modules.video.src.infrastructure_ffmpeg_video_adapter", "FFmpegVideoAdapter"
    )
    return cls()


def build_utils() -> Any:
    cls = _load_module(
        "modules.system_utils.src.infrastructure_system_utils_util", "SystemUtilsUtil"
    )
    return cls()


def build_image_processing(opencv: Any, tesseract: Any, llm: Any) -> Any:
    cls = _load_module(
        "modules.image.src.capabilities_image_processing_processor", "ImageProcessingProcessor"
    )
    return cls(opencv_port=opencv, tesseract_port=tesseract, llm_port=llm)


def build_video_processing(opencv: Any, ffmpeg: Any) -> Any:
    cls = _load_module(
        "modules.video.src.capabilities_video_processing_processor", "VideoProcessingProcessor"
    )
    return cls(opencv_port=opencv, ffmpeg_port=ffmpeg)


def build_video_analysis(opencv: Any) -> Any:
    cls = _load_module(
        "modules.video.src.capabilities_video_analysis_analyzer", "VideoAnalysisAnalyzer"
    )
    return cls(opencv_port=opencv)


def build_video_timeline(opencv: Any, video_proc: Any, analysis: Any) -> Any:
    cls = _load_module(
        "modules.video.src.capabilities_video_timeline_generator", "VideoTimelineGenerator"
    )
    return cls(opencv_port=opencv, video_cap=video_proc, analysis_cap=analysis)


def build_object_tracking(opencv: Any) -> Any:
    cls = _load_module(
        "modules.tracking.src.capabilities_object_tracking_tracker", "ObjectTrackingTracker"
    )
    return cls(opencv_port=opencv)


def build_visual_memory(opencv: Any, utils: Any) -> Any:
    cls = _load_module(
        "modules.memory.src.capabilities_visual_memory_repository", "VisualMemoryStore"
    )
    return cls(opencv_port=opencv, utils_port=utils)


def build() -> dict[str, Any]:
    opencv = build_opencv()
    tesseract = build_tesseract()
    llm = build_llm()
    ffmpeg = build_ffmpeg()
    utils = build_utils()

    image_proc = build_image_processing(opencv, tesseract, llm)
    video_proc = build_video_processing(opencv, ffmpeg)
    video_analysis = build_video_analysis(opencv)
    video_timeline = build_video_timeline(opencv, video_proc, video_analysis)
    obj_tracking = build_object_tracking(opencv)
    visual_mem = build_visual_memory(opencv, utils)

    return {
        "opencv": opencv,
        "tesseract": tesseract,
        "llm": llm,
        "ffmpeg": ffmpeg,
        "utils": utils,
        "image_processing": image_proc,
        "video_processing": video_proc,
        "video_analysis": video_analysis,
        "video_timeline": video_timeline,
        "object_tracking": obj_tracking,
        "visual_memory": visual_mem,
    }
