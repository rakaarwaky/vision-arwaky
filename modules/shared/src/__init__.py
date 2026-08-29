"""Shared layer barrel — re-exports all shared types (VO, event, error, constant, contract, utility)."""

from modules.shared.src.contract_ffmpeg_video_protocol import FFmpegVideoProtocol
from modules.shared.src.contract_image_processing_protocol import (
    ImageProcessingProtocol,
)
from modules.shared.src.contract_llm_vision_protocol import LLMVisionProtocol
from modules.shared.src.contract_object_tracking_protocol import (
    ObjectTrackingProtocol,
)
from modules.shared.src.contract_registry_service_aggregate import (
    RegistryServiceAggregate,
)
from modules.shared.src.contract_system_configuration_protocol import (
    SystemConfigurationProtocol,
)
from modules.shared.src.contract_system_job_protocol import SystemJobProtocol
from modules.shared.src.contract_tesseract_ocr_protocol import TesseractOCRProtocol
from modules.shared.src.contract_video_analysis_protocol import (
    VideoAnalysisProtocol,
)
from modules.shared.src.contract_video_processing_protocol import (
    VideoProcessingProtocol,
)
from modules.shared.src.contract_video_understanding_protocol import (
    VideoUnderstandingProtocol,
)
from modules.shared.src.contract_workspace_protocol import WorkspaceProtocol
from modules.shared.src.taxonomy_vision_constant import (
    EMBEDDED_SKILL_MD,
    FRAME_EXTRACTION_INTERVAL_S,
    MAX_EXTRACT_FRAMES,
    MAX_SMART_VIDEO_FRAMES,
    MAX_SUMMARY_PROMPT_CHARS,
    MAX_TRACK_FRAMES,
    MIN_MOTION_AREA,
    SCENE_THRESHOLD,
)
from modules.shared.src.taxonomy_vision_error import (
    DependencyExecutionError,
    ImageProcessingError,
    InvalidParameterError,
    VideoProcessingError,
    VisionDomainError,
)
from modules.shared.src.taxonomy_vision_event import (
    MotionEvent,
    SceneChange,
)
from modules.shared.src.taxonomy_vision_vo import (
    AnalysisPrompt,
    BackendType,
    BoundingBox,
    CommandName,
    CommandOutput,
    FilePath,
    FrameAnalysis,
    IntervalSeconds,
    LanguageCode,
    MaxFrames,
    MinArea,
    ModelName,
    MotionDirection,
    MotionMagnitude,
    OcrText,
    SceneThreshold,
    ScreenshotComparison,
    SimilarityScore,
    Timestamp,
    VideoInfo,
    VideoUnderstanding,
    VideoUnderstandingConfig,
    VisionAnalysis,
)
from modules.shared.src.taxonomy_xdg_paths_vo import (
    APP_NAME,
    XDGPaths,
)
from modules.shared.src.utility_async_runner import run_async
from modules.shared.src.utility_config_handler import (
    find_config,
    load_config,
    save_config,
    scan_models,
)
from modules.shared.src.utility_opencv_ops import (
    calc_optical_flow,
    check_video_corruption,
    compare_histograms,
    compute_abs_diff,
    compute_phash,
    detect_edges,
    find_contours,
    get_bounding_box,
    get_contour_area,
    get_video_metadata,
    open_video_capture,
    read_image,
    to_grayscale,
    write_image,
)
from modules.shared.src.utility_system_utils import (
    file_exists,
    get_ffmpeg_path,
    get_ffprobe_path,
    get_file_size_mb,
    validate_path,
)

__all__ = [
    "APP_NAME",
    "EMBEDDED_SKILL_MD",
    "FRAME_EXTRACTION_INTERVAL_S",
    "MAX_EXTRACT_FRAMES",
    "MAX_SMART_VIDEO_FRAMES",
    "MAX_SUMMARY_PROMPT_CHARS",
    "MAX_TRACK_FRAMES",
    "MIN_MOTION_AREA",
    "SCENE_THRESHOLD",
    "AnalysisPrompt",
    "BackendType",
    "BoundingBox",
    "CommandName",
    "CommandOutput",
    "DependencyExecutionError",
    "FFmpegVideoProtocol",
    "FilePath",
    "FrameAnalysis",
    "ImageProcessingError",
    "ImageProcessingProtocol",
    "IntervalSeconds",
    "InvalidParameterError",
    "LLMVisionProtocol",
    "LanguageCode",
    "MaxFrames",
    "MinArea",
    "ModelName",
    "MotionDirection",
    "MotionEvent",
    "MotionMagnitude",
    "ObjectTrackingProtocol",
    "OcrText",
    "RegistryServiceAggregate",
    "SceneChange",
    "SceneThreshold",
    "ScreenshotComparison",
    "SimilarityScore",
    "SystemConfigurationProtocol",
    "SystemJobProtocol",
    "TesseractOCRProtocol",
    "Timestamp",
    "VideoAnalysisProtocol",
    "VideoInfo",
    "VideoProcessingError",
    "VideoProcessingProtocol",
    "VideoUnderstanding",
    "VideoUnderstandingConfig",
    "VideoUnderstandingProtocol",
    "VisionAnalysis",
    "VisionDomainError",
    "WorkspaceProtocol",
    "XDGPaths",
    "calc_optical_flow",
    "check_video_corruption",
    "compare_histograms",
    "compute_abs_diff",
    "compute_phash",
    "detect_edges",
    "file_exists",
    "find_config",
    "find_contours",
    "get_bounding_box",
    "get_contour_area",
    "get_ffmpeg_path",
    "get_ffprobe_path",
    "get_file_size_mb",
    "get_video_metadata",
    "load_config",
    "open_video_capture",
    "read_image",
    "run_async",
    "save_config",
    "scan_models",
    "to_grayscale",
    "validate_path",
    "write_image",
]
