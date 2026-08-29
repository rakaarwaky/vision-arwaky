"""Video Agent Orchestrator — coordinates video processing, analysis, and timeline via DI."""

import json
from typing import Any

from modules.shared.src.contract_ffmpeg_video_protocol import FFmpegVideoProtocol
from modules.shared.src.contract_object_tracking_protocol import (
    ObjectTrackingProtocol,
)
from modules.shared.src.contract_opencv_image_protocol import OpenCVImageProtocol
from modules.shared.src.contract_registry_service_aggregate import (
    RegistryServiceAggregate,
)
from modules.shared.src.contract_video_analysis_protocol import (
    VideoAnalysisProtocol,
)
from modules.shared.src.contract_video_processing_protocol import (
    VideoProcessingProtocol,
)
from modules.shared.src.contract_video_timeline_protocol import (
    VideoTimelineProtocol,
)
from modules.shared.src.contract_video_understanding_protocol import (
    VideoUnderstandingProtocol,
)
from modules.shared.src.taxonomy_vision_models_vo import (
    AnalysisPrompt,
    BoundingBox,
    CommandName,
    CommandOutput,
    FilePath,
    IntervalSeconds,
    MaxFrames,
    MinArea,
    SceneThreshold,
    TimeSegment,
)
from modules.shared.src.utility_async_runner import run_async


class VideoOrchestrator(RegistryServiceAggregate):
    """Orchestrator for video processing domain (pure delegation facade)."""

    def __init__(
        self,
        video_processing: VideoProcessingProtocol,
        video_analysis: VideoAnalysisProtocol,
        video_timeline: VideoTimelineProtocol,
        object_tracking: ObjectTrackingProtocol,
        opencv: OpenCVImageProtocol,
        ffmpeg: FFmpegVideoProtocol,
        video_understanding: VideoUnderstandingProtocol,
    ):
        self._video_processing = video_processing
        self._video_analysis = video_analysis
        self._video_timeline = video_timeline
        self._object_tracking = object_tracking
        self._opencv = opencv
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
            interval_val = float(kwargs["interval"])
            interval = IntervalSeconds(value=interval_val)
            res = run_async(
                self._video_processing.extract_frames(
                    FilePath(value=kwargs["video"]), interval
                )
            )
            return CommandOutput(value=json.dumps([r.value for r in res], indent=2))
        elif command.value == "convert":
            inp = FilePath(value=kwargs["input_path"])
            out = FilePath(value=kwargs["output_path"])
            res = run_async(self._video_processing.convert_format(inp, out))
            return CommandOutput(value=json.dumps({"success": res}))
        elif command.value == "check-corruption":
            res = self._video_processing.check_corruption(
                FilePath(value=kwargs["video"])
            )
            return CommandOutput(value=json.dumps({"corrupted": res}))
        elif command.value == "create-gif":
            vid = FilePath(value=kwargs["video"])
            out = FilePath(value=kwargs["output_path"])
            start = float(kwargs["start"]) if kwargs["start"] else None
            duration = float(kwargs["duration"]) if kwargs["duration"] else None
            segment = TimeSegment(start=start, duration=duration)
            res = run_async(self._video_processing.create_gif(vid, out, segment))
            return CommandOutput(value=json.dumps({"success": res}))
        elif command.value == "detect-scenes":
            vid = FilePath(value=kwargs["video"])
            thresh_val = float(kwargs["threshold"])
            threshold = SceneThreshold(value=thresh_val)
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
            min_area_val = int(kwargs["min_area"])
            min_area = MinArea(value=min_area_val)
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
            max_frames_val = int(kwargs["max_frames"])
            max_frames = MaxFrames(value=max_frames_val)
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
        elif command.value == "timeline":
            vid = FilePath(value=kwargs["video"])
            interval = IntervalSeconds(value=float(kwargs["interval"]))
            return CommandOutput(
                value=json.dumps(
                    run_async(
                        self._video_timeline.generate_timeline(vid, interval)
                    ).model_dump(),
                    indent=2,
                )
            )
        elif command.value == "analyze-video":
            vid = FilePath(value=kwargs["video"])
            prompt = AnalysisPrompt(value=kwargs.get("prompt"))
            result = self._video_understanding.analyze(
                vid,
                prompt,
                interval=float(kwargs.get("interval", 30.0)),
                scene_threshold=float(kwargs.get("scene_threshold", 20.0)),
                min_area=int(kwargs.get("min_area", 500)),
            )
            return CommandOutput(value=json.dumps(result.model_dump(), indent=2))
        raise ValueError(f"Unknown video command: {command.value}")
