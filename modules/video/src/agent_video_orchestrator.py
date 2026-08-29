"""Video Agent Orchestrator — coordinates video processing, analysis, and tracking via DI."""

import json
from typing import Any

from modules.shared.src.contract_ffmpeg_video_protocol import FFmpegVideoProtocol
from modules.shared.src.contract_object_tracking_protocol import (
    ObjectTrackingProtocol,
)
from modules.shared.src.contract_registry_service_aggregate import (
    RegistryServiceAggregate,
)
from modules.shared.src.contract_video_analysis_protocol import (
    VideoAnalysisProtocol,
)
from modules.shared.src.contract_video_processing_protocol import (
    VideoProcessingProtocol,
)
from modules.shared.src.contract_video_understanding_protocol import (
    VideoUnderstandingProtocol,
)
from modules.shared.src.taxonomy_vision_constant import (
    FRAME_EXTRACTION_INTERVAL_S,
    MAX_TRACK_FRAMES,
    MIN_MOTION_AREA,
    SCENE_THRESHOLD,
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
)
from modules.shared.src.utility_async_runner import run_async


class VideoOrchestrator(RegistryServiceAggregate):
    """Orchestrator for video processing domain (pure delegation facade)."""

    def __init__(
        self,
        video_processing: VideoProcessingProtocol,
        video_analysis: VideoAnalysisProtocol,
        object_tracking: ObjectTrackingProtocol,
        ffmpeg: FFmpegVideoProtocol,
        video_understanding: VideoUnderstandingProtocol | None = None,
    ):
        self._video_processing = video_processing
        self._video_analysis = video_analysis
        self._object_tracking = object_tracking
        self._ffmpeg = ffmpeg
        self._video_understanding = video_understanding

    def execute_in_process(
        self,
        command: CommandName,
        kwargs: dict[str, Any],
    ) -> CommandOutput:
        """Execute video-related commands by delegating to injected capabilities."""
        if command.value == "video-info":
            vid = FilePath(value=kwargs["video"])
            return CommandOutput(
                value=json.dumps(
                    self._video_processing.get_info(vid).model_dump(), indent=2
                )
            )
        elif command.value == "extract-frames":
            interval = IntervalSeconds(
                value=kwargs.get("interval", FRAME_EXTRACTION_INTERVAL_S)
            )
            res = run_async(
                self._video_processing.extract_frames(
                    FilePath(value=kwargs["video"]), interval
                )
            )
            return CommandOutput(value=json.dumps([r.value for r in res], indent=2))
        elif command.value == "check-corruption":
            res = self._video_processing.check_corruption(
                FilePath(value=kwargs["video"])
            )
            return CommandOutput(value=json.dumps({"corrupted": res}))
        elif command.value == "detect-scenes":
            vid = FilePath(value=kwargs["video"])
            threshold = SceneThreshold(value=kwargs.get("threshold", SCENE_THRESHOLD))
            return CommandOutput(
                value=json.dumps(
                    [
                        s.model_dump()
                        for s in self._video_analysis.detect_scenes(vid, threshold)
                    ],
                    indent=2,
                )
            )
        elif command.value == "detect-motion":
            vid = FilePath(value=kwargs["video"])
            min_area = MinArea(value=kwargs.get("min_area", MIN_MOTION_AREA))
            return CommandOutput(
                value=json.dumps(
                    [
                        m.model_dump()
                        for m in self._video_analysis.detect_motion(vid, min_area)
                    ],
                    indent=2,
                )
            )
        elif command.value == "track":
            vid = FilePath(value=kwargs["video"])
            x, y, w, h = [int(v) for v in kwargs["bbox"].split(",")]
            bbox = BoundingBox(x=x, y=y, width=w, height=h)
            max_frames = MaxFrames(value=kwargs.get("max_frames", MAX_TRACK_FRAMES))
            return CommandOutput(
                value=json.dumps(
                    [
                        b.model_dump()
                        for b in self._object_tracking.track_object(
                            vid, bbox, max_frames
                        )
                    ],
                    indent=2,
                )
            )
        elif command.value == "analyze-video":
            if self._video_understanding is None:
                raise RuntimeError(
                    "Video understanding capability is not configured for analyze-video"
                )
            vid = FilePath(value=kwargs["video"])
            prompt = AnalysisPrompt(value=kwargs.get("prompt", ""))
            result = self._video_understanding.analyze(
                vid,
                prompt,
            )
            return CommandOutput(value=json.dumps(result.model_dump(), indent=2))
        raise ValueError(f"Unknown video command: {command.value}")
