from abc import ABC, abstractmethod
from src.taxonomy import CommandName, CommandOutput
from .image_processing_protocol import ImageProcessingProtocol
from .video_processing_protocol import VideoProcessingProtocol
from .video_analysis_protocol import VideoAnalysisProtocol
from .object_tracking_protocol import ObjectTrackingProtocol
from .visual_memory_protocol import VisualMemoryProtocol
from .video_timeline_protocol import VideoTimelineProtocol
from .opencv_image_port import OpenCVImagePort
from .tesseract_ocr_port import TesseractOCRPort
from .ffmpeg_video_port import FFmpegVideoPort
from .llm_vision_port import LLMVisionPort
from .system_utils_port import SystemUtilsPort


class RegistryServiceAggregate(ABC):
    """Dynamic Service Locator Aggregate for capabilities and adapters."""

    _instance = None

    @classmethod
    def get_instance(cls) -> "RegistryServiceAggregate":
        """Dynamic resolution of the concrete agent/orchestrator class."""
        if cls._instance is None:
            import importlib
            module = importlib.import_module("src.agent.vision_agent_orchestrator")
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
    def execute_in_process(cls, command: CommandName, kwargs: dict) -> CommandOutput:
        """Route and execute any command in-process across domains."""
        ...
