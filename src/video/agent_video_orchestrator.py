"""Video Agent Orchestrator — coordinates video processing, analysis, and timeline."""

import asyncio
import importlib
import json
from typing import Any, Dict

from src.shared.vision_models_vo import (
    FilePath, TimeSegment, SceneThreshold,
    MinArea, BoundingBox, IntervalSeconds, MaxFrames,
)


class VideoOrchestrator:
    """Orchestrator for video processing domain."""

    @staticmethod
    def get_opencv():
        module = importlib.import_module("src.opencv.infrastructure_opencv_image_adapter")
        cls = getattr(module, "OpenCVImageAdapter")
        return cls()

    @staticmethod
    def get_ffmpeg():
        module = importlib.import_module("src.video.infrastructure_ffmpeg_video_adapter")
        cls = getattr(module, "FFmpegVideoAdapter")
        return cls()

    @staticmethod
    def get_video_processing():
        cap_mod = importlib.import_module("src.video.capabilities_video_processing_processor")
        cap_cls = getattr(cap_mod, "VideoProcessingProcessor")
        return cap_cls(
            opencv_port=VideoOrchestrator.get_opencv(),
            ffmpeg_port=VideoOrchestrator.get_ffmpeg(),
        )

    @staticmethod
    def get_video_analysis():
        cap_mod = importlib.import_module("src.video.capabilities_video_analysis_analyzer")
        cap_cls = getattr(cap_mod, "VideoAnalysisAnalyzer")
        return cap_cls(
            opencv_port=VideoOrchestrator.get_opencv(),
        )

    @staticmethod
    def get_video_timeline():
        cap_mod = importlib.import_module("src.video.capabilities_video_timeline_generator")
        cap_cls = getattr(cap_mod, "VideoTimelineGenerator")
        return cap_cls(
            opencv_port=VideoOrchestrator.get_opencv(),
            video_cap=VideoOrchestrator.get_video_processing(),
            analysis_cap=VideoOrchestrator.get_video_analysis(),
        )

    @staticmethod
    def get_object_tracking():
        cap_mod = importlib.import_module("src.tracking.capabilities_object_tracking_tracker")
        cap_cls = getattr(cap_mod, "ObjectTrackingTracker")
        return cap_cls(
            opencv_port=VideoOrchestrator.get_opencv(),
        )

    @staticmethod
    def _run_async(coro):
        """Run an async coroutine safely, handling existing event loops."""
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # No running loop — safe to use asyncio.run()
            return asyncio.run(coro)
        # Already have a running loop — use Runner()
        with asyncio.Runner() as runner:
            return runner.run(coro)

    @staticmethod
    def execute_video_cmd(command: str, kwargs: Dict[str, Any]) -> str | None:
        """Execute video-related commands."""
        if command == "video-info":
            vid = FilePath(value=kwargs["video"])
            return json.dumps(
                VideoOrchestrator.get_video_processing().get_info(vid).model_dump(), indent=2
            )
        elif command == "extract-frames":
            interval_val = float(kwargs["interval"])
            interval = IntervalSeconds(value=interval_val)
            res = VideoOrchestrator._run_async(
                VideoOrchestrator.get_video_processing().extract_frames(
                    FilePath(value=kwargs["video"]), interval
                )
            )
            return json.dumps([r.value for r in res], indent=2)
        elif command == "convert":
            inp = FilePath(value=kwargs["input_path"])
            out = FilePath(value=kwargs["output_path"])
            res = VideoOrchestrator._run_async(
                VideoOrchestrator.get_video_processing().convert_format(inp, out)
            )
            return json.dumps({"success": res})
        elif command == "check-corruption":
            res = VideoOrchestrator.get_video_processing().check_corruption(
                FilePath(value=kwargs["video"])
            )
            return json.dumps({"corrupted": res})
        elif command == "create-gif":
            vid = FilePath(value=kwargs["video"])
            out = FilePath(value=kwargs["output_path"])
            start = float(kwargs["start"]) if kwargs["start"] else None
            duration = float(kwargs["duration"]) if kwargs["duration"] else None
            segment = TimeSegment(start=start, duration=duration)
            res = VideoOrchestrator._run_async(
                VideoOrchestrator.get_video_processing().create_gif(vid, out, segment)
            )
            return json.dumps({"success": res})
        elif command == "detect-scenes":
            vid = FilePath(value=kwargs["video"])
            thresh_val = float(kwargs["threshold"])
            threshold = SceneThreshold(value=thresh_val)
            return json.dumps(
                [
                    s.model_dump()
                    for s in VideoOrchestrator.get_video_analysis().detect_scenes(vid, threshold)
                ],
                indent=2,
            )
        elif command == "detect-motion":
            vid = FilePath(value=kwargs["video"])
            min_area_val = int(kwargs["min_area"])
            min_area = MinArea(value=min_area_val)
            return json.dumps(
                [
                    m.model_dump()
                    for m in VideoOrchestrator.get_video_analysis().detect_motion(vid, min_area)
                ],
                indent=2,
            )
        elif command == "track":
            vid = FilePath(value=kwargs["video"])
            x, y, w, h = [int(v) for v in kwargs["bbox"].split(",")]
            bbox = BoundingBox(x=x, y=y, width=w, height=h)
            max_frames_val = int(kwargs["max_frames"])
            max_frames = MaxFrames(value=max_frames_val)
            return json.dumps(
                [
                    b.model_dump()
                    for b in VideoOrchestrator.get_object_tracking().track_object(
                        vid, bbox, max_frames
                    )
                ],
                indent=2,
            )
        elif command == "timeline":
            vid = FilePath(value=kwargs["video"])
            interval_val = int(kwargs["interval"])
            interval = IntervalSeconds(value=float(interval_val))
            return json.dumps(
                VideoOrchestrator._run_async(
                    VideoOrchestrator.get_video_timeline().generate_timeline(vid, interval)
                ).model_dump(),
                indent=2,
            )
        return None
