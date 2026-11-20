"""Shared layer barrel — re-exports all shared types (VO, error, constant, contract, utility)."""

from modules.shared.src.common.taxonomy_command_vo import (
    ALL_COMMANDS,
    IMAGE_COMMANDS,
    SYSTEM_COMMANDS,
    VIDEO_COMMANDS,
    CommandDomain,
)
from modules.shared.src.common.taxonomy_vision_constant import (
    ANALYZE_VIDEO_INTERVAL_S,
    DEFAULT_MODELS_TIMEOUT_S,
    DEFAULT_VIDEO_FPS,
    DEFAULT_VLM_MAX_TOKENS,
    DEFAULT_VLM_TEMPERATURE,
    DEFAULT_VLM_TIMEOUT_S,
    FFMPEG_TIMEOUT_S,
    MAX_SMART_VIDEO_FRAMES,
    MAX_SUMMARY_PROMPT_CHARS,
)
from modules.shared.src.common.taxonomy_vision_error import (
    DependencyExecutionError,
    ImageProcessingError,
    InvalidParameterError,
    VideoProcessingError,
    VisionDomainError,
)
from modules.shared.src.common.taxonomy_vision_vo import (
    AnalysisPrompt,
    BackendType,
    CommandName,
    CommandOutput,
    ConfigKey,
    FilePath,
    FrameAnalysis,
    ModelName,
    VideoUnderstanding,
    VideoUnderstandingConfig,
    VisionAnalysis,
)
from modules.shared.src.common.taxonomy_xdg_paths_vo import (
    APP_NAME,
    XDGPaths,
)
from modules.shared.src.common.utility_command_output import (
    dict_to_command_output,
    to_command_output,
)
from modules.shared.src.common.utility_config_handler import (
    find_active_config,
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
from modules.shared.src.common.utility_dependency_checker import (
    check_all_dependencies,
)
from modules.shared.src.common.utility_llm_check import check_llm_endpoint, list_models
from modules.shared.src.common.utility_opencv_ops import (
    open_video_capture,
    read_image,
    resize_image,
    to_grayscale,
    write_image,
)
from modules.shared.src.common.utility_version_resolver import get_package_version
from modules.shared.src.common.utility_xdg_paths import ensure_xdg_dirs
from modules.shared.src.contract_registry_service_aggregate import (
    IRegistryServiceAggregate,
)
from modules.shared.src.image.contract_image_processing_protocol import (
    IImageProcessingProtocol,
)
from modules.shared.src.image.contract_llm_vision_protocol import ILLMVisionProtocol
from modules.shared.src.system.contract_system_configuration_protocol import (
    ISystemConfigurationProtocol,
)
from modules.shared.src.system.contract_system_job_protocol import ISystemJobProtocol
from modules.shared.src.system.contract_workspace_protocol import IWorkspaceProtocol
from modules.shared.src.video.contract_video_understanding_protocol import (
    IVideoUnderstandingProtocol,
)

__all__ = [
    "ALL_COMMANDS",
    "ANALYZE_VIDEO_INTERVAL_S",
    "APP_NAME",
    "DEFAULT_MODELS_TIMEOUT_S",
    "DEFAULT_VIDEO_FPS",
    "DEFAULT_VLM_MAX_TOKENS",
    "DEFAULT_VLM_TEMPERATURE",
    "DEFAULT_VLM_TIMEOUT_S",
    "FFMPEG_TIMEOUT_S",
    "IMAGE_COMMANDS",
    "MAX_SMART_VIDEO_FRAMES",
    "MAX_SUMMARY_PROMPT_CHARS",
    "SYSTEM_COMMANDS",
    "VIDEO_COMMANDS",
    "AnalysisPrompt",
    "BackendType",
    "CommandDomain",
    "CommandName",
    "CommandOutput",
    "ConfigKey",
    "DependencyExecutionError",
    "FilePath",
    "FrameAnalysis",
    "IImageProcessingProtocol",
    "ILLMVisionProtocol",
    "IRegistryServiceAggregate",
    "ISystemConfigurationProtocol",
    "ISystemJobProtocol",
    "IVideoUnderstandingProtocol",
    "IWorkspaceProtocol",
    "ImageProcessingError",
    "InvalidParameterError",
    "ModelName",
    "VideoProcessingError",
    "VideoUnderstanding",
    "VideoUnderstandingConfig",
    "VisionAnalysis",
    "VisionDomainError",
    "XDGPaths",
    "check_all_dependencies",
    "check_llm_endpoint",
    "dict_to_command_output",
    "ensure_xdg_dirs",
    "find_active_config",
    "get_local_config_path",
    "get_package_version",
    "get_user_config_path",
    "load_config",
    "load_merged_config",
    "list_models",
    "open_video_capture",
    "read_image",
    "read_yaml_config",
    "resize_image",
    "resolve_external_settings",
    "save_config",
    "save_user_config",
    "scan_models",
    "to_command_output",
    "to_grayscale",
    "write_image",
]
