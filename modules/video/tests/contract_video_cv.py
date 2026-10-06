"""Contract tests: video feature implements shared protocols and aggregate."""

import inspect

from modules.shared.src.contract_ffmpeg_video_protocol import IFFmpegVideoProtocol
from modules.shared.src.contract_object_tracking_protocol import (
    IObjectTrackingProtocol,
)
from modules.shared.src.contract_registry_service_aggregate import (
    IRegistryServiceAggregate,
)
from modules.shared.src.contract_video_analysis_protocol import (
    IVideoAnalysisProtocol,
)
from modules.shared.src.contract_video_processing_protocol import (
    IVideoProcessingProtocol,
)
from modules.shared.src.contract_video_understanding_protocol import (
    IVideoUnderstandingProtocol,
)
from modules.video.src.agent_video_orchestrator import VideoOrchestrator
from modules.video.src.capabilities_ffmpeg_adapter import FFmpegVideoAdapter
from modules.video.src.capabilities_object_tracker import ObjectTrackingTracker
from modules.video.src.capabilities_video_analyzer import VideoAnalysisAnalyzer
from modules.video.src.capabilities_video_processor import (
    VideoProcessingProcessor,
)
from modules.video.src.capabilities_video_understanding import (
    VideoUnderstandingAnalyzer,
)


class TestVideoContracts:
    def test_processor_implements_protocol(self):
        assert issubclass(VideoProcessingProcessor, IVideoProcessingProtocol)

    def test_analyzer_implements_protocol(self):
        assert issubclass(VideoAnalysisAnalyzer, IVideoAnalysisProtocol)

    def test_tracker_implements_protocol(self):
        assert issubclass(ObjectTrackingTracker, IObjectTrackingProtocol)

    def test_tracker_exposes_track_object(self):
        methods = {
            name
            for name, _ in inspect.getmembers(ObjectTrackingTracker, inspect.isfunction)
            if not name.startswith("_")
        }
        assert "track_object" in methods

    def test_understanding_implements_protocol(self):
        assert issubclass(VideoUnderstandingAnalyzer, IVideoUnderstandingProtocol)

    def test_ffmpeg_adapter_implements_protocol(self):
        assert issubclass(FFmpegVideoAdapter, IFFmpegVideoProtocol)

    def test_orchestrator_implements_aggregate(self):
        assert issubclass(VideoOrchestrator, IRegistryServiceAggregate)

    def test_processor_public_methods_present(self):
        methods = {
            name
            for name, _ in inspect.getmembers(
                VideoProcessingProcessor, inspect.isfunction
            )
            if not name.startswith("_")
        }
        assert "get_info" in methods
        assert "check_corruption" in methods

    def test_ffmpeg_adapter_instantiable(self):
        assert isinstance(FFmpegVideoAdapter(), object)
