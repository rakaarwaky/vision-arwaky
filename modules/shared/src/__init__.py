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
from modules.shared.src.taxonomy_command_vo import (
    ALL_COMMANDS,
    IMAGE_COMMANDS,
    SYSTEM_COMMANDS,
    VIDEO_COMMANDS,
    CommandDomain,
)
from modules.shared.src.taxonomy_vision_constant import (
    EMBEDDED_SKILL_MD,
    FFMPEG_TIMEOUT_S,
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
    ConfigKey,
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
from modules.shared.src.utility_command_output import (
    dict_to_command_output,
    to_command_output,
    to_command_output_list,
)
from modules.shared.src.utility_config_handler import (
    find_active_config,
    find_config,
    get_local_config_path,
    get_user_config_path,
    load_config,
    load_merged_config,
    read_yaml_config,
    resolve_external_settings,
    save_config,
    save_user_config,
    scan_models,
)
from modules.shared.src.utility_dependency_checker import (
    check_all_dependencies,
    check_binary_dependencies,
    check_python_dependencies,
)
from modules.shared.src.utility_frame_extractor import (
    extract_frames_at_indices,
    extract_middle_frame,
)
from modules.shared.src.utility_llm_check import check_llm_endpoint
from modules.shared.src.utility_opencv_ops import (
    apply_dilate,
    apply_gaussian_blur,
    apply_threshold,
    calc_optical_flow,
    check_video_corruption,
    compare_histograms,
    compute_abs_diff,
    compute_histogram_hsv,
    compute_moments,
    compute_phash,
    detect_edges,
    find_contours,
    get_bounding_box,
    get_contour_area,
    get_video_metadata,
    open_video_capture,
    pad_image_border,
    read_image,
    resize_image,
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
from modules.shared.src.utility_version_resolver import get_package_version
from modules.shared.src.utility_xdg_paths import ensure_xdg_dirs

__all__ = [
    "ALL_COMMANDS",
    "APP_NAME",
    "EMBEDDED_SKILL_MD",
    "FFMPEG_TIMEOUT_S",
    "FRAME_EXTRACTION_INTERVAL_S",
    "IMAGE_COMMANDS",
    "MAX_EXTRACT_FRAMES",
    "MAX_SMART_VIDEO_FRAMES",
    "MAX_SUMMARY_PROMPT_CHARS",
    "MAX_TRACK_FRAMES",
    "MIN_MOTION_AREA",
    "SCENE_THRESHOLD",
    "SYSTEM_COMMANDS",
    "VIDEO_COMMANDS",
    "AnalysisPrompt",
    "BackendType",
    "BoundingBox",
    "CommandDomain",
    "CommandName",
    "CommandOutput",
    "ConfigKey",
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
    "apply_dilate",
    "apply_gaussian_blur",
    "apply_threshold",
    "calc_optical_flow",
    "check_all_dependencies",
    "check_binary_dependencies",
    "check_llm_endpoint",
    "check_python_dependencies",
    "check_video_corruption",
    "compare_histograms",
    "compute_abs_diff",
    "compute_histogram_hsv",
    "compute_moments",
    "compute_phash",
    "detect_edges",
    "dict_to_command_output",
    "ensure_xdg_dirs",
    "extract_frames_at_indices",
    "extract_middle_frame",
    "file_exists",
    "find_active_config",
    "find_config",
    "find_contours",
    "get_bounding_box",
    "get_contour_area",
    "get_ffmpeg_path",
    "get_ffprobe_path",
    "get_file_size_mb",
    "get_local_config_path",
    "get_package_version",
    "get_user_config_path",
    "get_video_metadata",
    "load_config",
    "load_merged_config",
    "open_video_capture",
    "pad_image_border",
    "read_image",
    "read_yaml_config",
    "resize_image",
    "resolve_external_settings",
    "run_async",
    "save_config",
    "save_user_config",
    "scan_models",
    "to_command_output",
    "to_command_output_list",
    "to_grayscale",
    "validate_path",
    "write_image",
]
