from abc import ABC, abstractmethod

from modules.shared.src.common.taxonomy_vision_models_vo import CommandName, CommandOutput
from .contract_image_processing_protocol import ImageProcessingProtocol
from .contract_video_processing_protocol import VideoProcessingProtocol
from .contract_video_analysis_protocol import VideoAnalysisProtocol
from modules.shared.src.video.contract_object_tracking_protocol import ObjectTrackingProtocol
from .contract_visual_memory_protocol import VisualMemoryProtocol
from .contract_video_timeline_protocol import VideoTimelineProtocol
from .contract_opencv_image_protocol import OpenCVImageProtocol
from .contract_tesseract_ocr_protocol import TesseractOCRProtocol
from .contract_ffmpeg_video_protocol import FFmpegVideoProtocol
from .contract_llm_vision_protocol import LLMVisionProtocol
from .contract_system_utils_protocol import SystemUtilsProtocol


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
    def get_utils() -> SystemUtilsProtocol:
        """Instantiate concrete Utils adapter dynamically."""
        ...

    @staticmethod
    @abstractmethod
    def get_opencv() -> OpenCVImageProtocol:
        """Instantiate concrete OpenCV adapter dynamically."""
        ...

    @staticmethod
    @abstractmethod
    def get_tesseract() -> TesseractOCRProtocol:
        """Instantiate concrete Tesseract adapter dynamically."""
        ...

    @staticmethod
    @abstractmethod
    def get_ffmpeg() -> FFmpegVideoProtocol:
        """Instantiate concrete FFmpeg adapter dynamically."""
        ...

    @staticmethod
    @abstractmethod
    def get_llm() -> LLMVisionProtocol:
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
