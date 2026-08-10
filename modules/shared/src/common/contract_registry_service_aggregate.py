from abc import ABC, abstractmethod
from modules.shared.src.common.taxonomy_vision_models_vo import CommandOutput, CommandName, CommandOutput
from .contract_image_processing_protocol import ImageProcessingProtocol
from .contract_video_processing_protocol import VideoProcessingProtocol
from .contract_video_analysis_protocol import VideoAnalysisProtocol
from .contract_object_tracking_protocol import ObjectTrackingProtocol
from .contract_visual_memory_protocol import VisualMemoryProtocol
from .contract_video_timeline_protocol import VideoTimelineProtocol
from .contract_opencv_image_protocol import OpenCVImagePort
from .contract_tesseract_ocr_protocol import TesseractOCRPort
from .contract_ffmpeg_video_protocol import FFmpegVideoPort
from .contract_llm_vision_protocol import LLMVisionPort
from .contract_system_utils_protocol import SystemUtilsPort


class RegistryServiceAggregate(ABC):
    """Dynamic Service Locator Aggregate for capabilities and adapters."""

    _instance = None

    @classmethod
    def get_instance(cls) -> "RegistryServiceAggregate":
        """Dynamic resolution of the concrete agent/orchestrator class."""
        if cls._instance is None:
            import importlib
            module = importlib.import_module("modules.agent.vision_agent_orchestrator")
            concrete_cls = getattr(module, "VisionAgentOrchestrator")
            cls._instance = concrete_cls()
        return cls._instance

    @staticmethod
    @abstractmethod
    def get_utils() -> SystemUtilsPort:
        """Instantiate concrete Utils adapter dynamically."""
        ...

    @staticmethod
    @abstractmethod
    def get_opencv() -> OpenCVImagePort:
        """Instantiate concrete OpenCV adapter dynamically."""
        ...

    @staticmethod
    @abstractmethod
    def get_tesseract() -> TesseractOCRPort:
        """Instantiate concrete Tesseract adapter dynamically."""
        ...

    @staticmethod
    @abstractmethod
    def get_ffmpeg() -> FFmpegVideoPort:
        """Instantiate concrete FFmpeg adapter dynamically."""
        ...

    @staticmethod
    @abstractmethod
    def get_llm() -> LLMVisionPort:
        """Instantiate concrete LLM adapter dynamically."""
        ...

    @staticmethod
    @abstractmethod
    def get_image_processing() -> ImageProcessingProtocol:
        """Instantiate concrete ImageProcessingProcessor dynamically with injected ports."""
        ...

    @staticmethod
    @abstractmethod
    def get_video_processing() -> VideoProcessingProtocol:
        """Instantiate concrete VideoProcessingProcessor dynamically with injected ports."""
        ...

    @staticmethod
    @abstractmethod
    def get_video_analysis() -> VideoAnalysisProtocol:
        """Instantiate concrete VideoAnalysisAnalyzer dynamically with injected ports."""
        ...

    @staticmethod
    @abstractmethod
    def get_object_tracking() -> ObjectTrackingProtocol:
        """Instantiate concrete ObjectTrackingTracker dynamically with injected ports."""
        ...

    @staticmethod
    @abstractmethod
    def get_visual_memory() -> VisualMemoryProtocol:
        """Instantiate concrete VisualMemoryStore dynamically with injected ports."""
        ...

    @staticmethod
    @abstractmethod
    def get_video_timeline() -> VideoTimelineProtocol:
        """Instantiate concrete VideoTimelineGenerator dynamically with injected ports."""
        ...

    @classmethod
    @abstractmethod
    def execute_in_process(cls, command: CommandName, kwargs: CommandOutput) -> CommandOutput:
        """Route and execute any command in-process across domains."""
        ...
