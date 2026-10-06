"""Video Agent Orchestrator — coordinates video processing, analysis, and tracking via DI."""

import json

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
from modules.shared.src.taxonomy_vision_constant import (
    FRAME_EXTRACTION_INTERVAL_S,
    MAX_TRACK_FRAMES,
    MIN_MOTION_AREA,
    SCENE_THRESHOLD,
)
from modules.shared.src.taxonomy_vision_error import (
    InvalidParameterError,
)
from modules.shared.src.taxonomy_vision_vo import (
    AnalysisPrompt,
    BoundingBox,
    CommandName,
    CommandOutput,
    FilePath,
    IntervalSeconds,
    MaxFrames,
    MinArea,
    SceneThreshold,
    SystemCommandParams,
)
from modules.shared.src.utility_async_runner import run_async
from modules.shared.src.utility_command_output import (
    to_command_output,
    to_command_output_list,
)


class VideoOrchestrator(IRegistryServiceAggregate):
    """Orchestrator for video processing domain (pure delegation facade)."""

    def __init__(
        self,
        video_processing: IVideoProcessingProtocol,
        video_analysis: IVideoAnalysisProtocol,
        object_tracking: IObjectTrackingProtocol,
        video_understanding: IVideoUnderstandingProtocol | None = None,
    ):
        self._video_processing = video_processing
        self._video_analysis = video_analysis
        self._object_tracking = object_tracking
        self._video_understanding = video_understanding

    def execute_in_process(
        self,
        command: CommandName,
        kwargs: dict | SystemCommandParams,
    ) -> CommandOutput:
        """Execute video-related commands by delegating to injected capabilities."""
        kw = kwargs if isinstance(kwargs, dict) else kwargs.model_dump()
        if command.value == "video-info":
            vid = FilePath.from_str(kw["video"])
            info = self._video_processing.get_info(vid)
            return to_command_output(info)
        elif command.value == "extract-frames":
            interval = IntervalSeconds(
                value=kw.get("interval", FRAME_EXTRACTION_INTERVAL_S)
            )
            res = run_async(
                self._video_processing.extract_frames(
                    FilePath.from_str(kw["video"]), interval
                )
            )
            return to_command_output_list(res)
        elif command.value == "check-corruption":
            corrupted = self._video_processing.check_corruption(
                FilePath.from_str(kw["video"])
            )
            return CommandOutput(value=json.dumps({"corrupted": corrupted}))
        elif command.value == "detect-scenes":
            vid = FilePath.from_str(kw["video"])
            threshold = SceneThreshold(value=kw.get("threshold", SCENE_THRESHOLD))
            scenes = self._video_analysis.detect_scenes(vid, threshold)
            return to_command_output_list(scenes)
        elif command.value == "detect-motion":
            vid = FilePath.from_str(kw["video"])
            min_area = MinArea(value=kw.get("min_area", MIN_MOTION_AREA))
            events = self._video_analysis.detect_motion(vid, min_area)
            return to_command_output_list(events)
        elif command.value == "track":
            vid = FilePath.from_str(kw["video"])
            parts = kw["bbox"].split(",")
            if len(parts) != 4:
                raise InvalidParameterError("bbox must be exactly 'X,Y,W,H'")
            x, y, w, h = (int(v) for v in parts)
            bbox = BoundingBox(x=x, y=y, width=w, height=h)
            if bbox.width <= 0 or bbox.height <= 0:
                raise InvalidParameterError("bbox width and height must be positive")
            max_frames = MaxFrames(value=kw.get("max_frames", MAX_TRACK_FRAMES))
            boxes = self._object_tracking.track_object(vid, bbox, max_frames)
            return to_command_output_list(boxes)
        elif command.value == "analyze-video":
            if self._video_understanding is None:
                raise InvalidParameterError(
                    "Video understanding capability is not configured for analyze-video"
                )
            vid = FilePath.from_str(kw["video"])
            prompt = AnalysisPrompt(value=kw.get("prompt", ""))
            result = self._video_understanding.analyze(
                vid,
                prompt,
            )
            return to_command_output(result)
        raise InvalidParameterError(f"Unknown video command: {command.value}")
