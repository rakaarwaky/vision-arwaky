"""Vision Agent Orchestrator — dynamic Application Orchestrator and service locator."""

import importlib
import asyncio
import json
from typing import Any, Dict

from src.taxonomy import (
    FilePath,
    LanguageCode,
    TimeSegment,
    BoundingBox,
    CommandName,
    CommandOutput,
    MemoryLabel,
    DistanceThreshold,
    SceneThreshold,
    MinArea,
    AnalysisPrompt,
    IntervalSeconds,
    MaxFrames,
)
from src.contract import (
    RegistryServiceAggregate,
    SystemUtilsPort,
    OpenCVImagePort,
    TesseractOCRPort,
    FFmpegVideoPort,
    LLMVisionPort,
    ImageProcessingProtocol,
    VideoProcessingProtocol,
    VideoAnalysisProtocol,
    ObjectTrackingProtocol,
    VisualMemoryProtocol,
    VideoTimelineProtocol,
)


class VisionAgentOrchestrator(RegistryServiceAggregate):
    """Orchestrator and locator for Vision capabilities."""

    @staticmethod
    def get_utils() -> SystemUtilsPort:
        """Instantiate concrete Utils adapter dynamically."""
        module = importlib.import_module("src.infrastructure.system_utils_util")
        cls = getattr(module, "SystemUtilsUtil")
        return cls()

    @staticmethod
    def get_opencv() -> OpenCVImagePort:
        """Instantiate concrete OpenCV adapter dynamically."""
        module = importlib.import_module("src.infrastructure.opencv_image_adapter")
        cls = getattr(module, "OpenCVImageAdapter")
        return cls()

    @staticmethod
    def get_tesseract() -> TesseractOCRPort:
        """Instantiate concrete Tesseract adapter dynamically."""
        module = importlib.import_module("src.infrastructure.tesseract_ocr_adapter")
        cls = getattr(module, "TesseractOCRAdapter")
        return cls()

    @staticmethod
    def get_ffmpeg() -> FFmpegVideoPort:
        """Instantiate concrete FFmpeg adapter dynamically."""
        module = importlib.import_module("src.infrastructure.ffmpeg_video_adapter")
        cls = getattr(module, "FFmpegVideoAdapter")
        return cls()

    @staticmethod
    def get_llm() -> LLMVisionPort:
        """Instantiate concrete LLM adapter dynamically."""
        module = importlib.import_module("src.infrastructure.llm_vision_adapter")
        cls = getattr(module, "LLMVisionAdapter")
        return cls()

    @staticmethod
    def get_image_processing() -> ImageProcessingProtocol:
        """Instantiate concrete ImageProcessingProcessor dynamically with injected ports."""
        cap_mod = importlib.import_module("src.capabilities.image_processing_processor")
        cap_cls = getattr(cap_mod, "ImageProcessingProcessor")
        return cap_cls(
            opencv_port=VisionAgentOrchestrator.get_opencv(),
            tesseract_port=VisionAgentOrchestrator.get_tesseract(),
            llm_port=VisionAgentOrchestrator.get_llm(),
        )

    @staticmethod
    def get_video_processing() -> VideoProcessingProtocol:
        """Instantiate concrete VideoProcessingProcessor dynamically with injected ports."""
        cap_mod = importlib.import_module("src.capabilities.video_processing_processor")
        cap_cls = getattr(cap_mod, "VideoProcessingProcessor")
        return cap_cls(
            opencv_port=VisionAgentOrchestrator.get_opencv(),
            ffmpeg_port=VisionAgentOrchestrator.get_ffmpeg(),
        )

    @staticmethod
    def get_video_analysis() -> VideoAnalysisProtocol:
        """Instantiate concrete VideoAnalysisAnalyzer dynamically with injected ports."""
        cap_mod = importlib.import_module("src.capabilities.video_analysis_analyzer")
        cap_cls = getattr(cap_mod, "VideoAnalysisAnalyzer")
        return cap_cls(
            opencv_port=VisionAgentOrchestrator.get_opencv(),
        )

    @staticmethod
    def get_object_tracking() -> ObjectTrackingProtocol:
        """Instantiate concrete ObjectTrackingTracker dynamically with injected ports."""
        cap_mod = importlib.import_module("src.capabilities.object_tracking_tracker")
        cap_cls = getattr(cap_mod, "ObjectTrackingTracker")
        return cap_cls(
            opencv_port=VisionAgentOrchestrator.get_opencv(),
        )

    @staticmethod
    def get_visual_memory() -> VisualMemoryProtocol:
        """Instantiate concrete VisualMemoryStore dynamically with injected ports."""
        cap_mod = importlib.import_module("src.capabilities.visual_memory_store")
        cap_cls = getattr(cap_mod, "VisualMemoryStore")
        return cap_cls(
            opencv_port=VisionAgentOrchestrator.get_opencv(),
            utils_port=VisionAgentOrchestrator.get_utils(),
        )

    @staticmethod
    def get_video_timeline() -> VideoTimelineProtocol:
        """Instantiate concrete VideoTimelineGenerator dynamically with injected ports."""
        cap_mod = importlib.import_module("src.capabilities.video_timeline_generator")
        cap_cls = getattr(cap_mod, "VideoTimelineGenerator")
        return cap_cls(
            opencv_port=VisionAgentOrchestrator.get_opencv(),
            video_cap=VisionAgentOrchestrator.get_video_processing(),
            analysis_cap=VisionAgentOrchestrator.get_video_analysis(),
        )

    @staticmethod
    def _execute_image_cmd(command: str, kwargs: Dict[str, Any]) -> str | None:
        if command == "analyze":
            img = FilePath(value=kwargs["image"])
            prompt_val = kwargs.get("prompt")
            prompt = AnalysisPrompt(value=prompt_val)
            return json.dumps(VisionAgentOrchestrator.get_image_processing().analyze_screenshot(img, prompt).model_dump(), indent=2)
        elif command == "ocr":
            img = FilePath(value=kwargs["image"])
            lang_val = kwargs.get("lang") or "eng"
            lang = LanguageCode(value=lang_val)
            return VisionAgentOrchestrator.get_image_processing().extract_text(img, lang).value
        elif command == "elements":
            img = FilePath(value=kwargs["image"])
            return json.dumps([e.model_dump() for e in VisionAgentOrchestrator.get_image_processing().find_elements(img)], indent=2)
        elif command == "compare":
            img1 = FilePath(value=kwargs["image1"])
            img2 = FilePath(value=kwargs["image2"])
            return json.dumps(VisionAgentOrchestrator.get_image_processing().compare_screenshots(img1, img2), indent=2)
        return None

    @staticmethod
    def _cmd_video_info(kwargs: Dict[str, Any]) -> str:
        vid = FilePath(value=kwargs["video"])
        return json.dumps(VisionAgentOrchestrator.get_video_processing().get_info(vid).model_dump(), indent=2)

    @staticmethod
    def _cmd_extract_frames(kwargs: Dict[str, Any]) -> str:
        interval_val = float(kwargs["interval"])
        interval = IntervalSeconds(value=interval_val)
        res = asyncio.run(VisionAgentOrchestrator.get_video_processing().extract_frames(FilePath(value=kwargs["video"]), interval))
        return json.dumps([r.value for r in res], indent=2)

    @staticmethod
    def _cmd_convert(kwargs: Dict[str, Any]) -> str:
        inp = FilePath(value=kwargs["input_path"])
        out = FilePath(value=kwargs["output_path"])
        res = asyncio.run(VisionAgentOrchestrator.get_video_processing().convert_format(inp, out))
        return json.dumps({"success": res})

    @staticmethod
    def _cmd_check_corruption(kwargs: Dict[str, Any]) -> str:
        res = VisionAgentOrchestrator.get_video_processing().check_corruption(FilePath(value=kwargs["video"]))
        return json.dumps({"corrupted": res})

    @staticmethod
    def _cmd_create_gif(kwargs: Dict[str, Any]) -> str:
        vid = FilePath(value=kwargs["video"])
        out = FilePath(value=kwargs["output_path"])
        start = float(kwargs["start"]) if kwargs["start"] else None
        duration = float(kwargs["duration"]) if kwargs["duration"] else None
        segment = TimeSegment(start=start, duration=duration)
        res = asyncio.run(VisionAgentOrchestrator.get_video_processing().create_gif(vid, out, segment))
        return json.dumps({"success": res})

    @staticmethod
    def _cmd_detect_scenes(kwargs: Dict[str, Any]) -> str:
        vid = FilePath(value=kwargs["video"])
        thresh_val = float(kwargs["threshold"])
        threshold = SceneThreshold(value=thresh_val)
        return json.dumps([s.model_dump() for s in VisionAgentOrchestrator.get_video_analysis().detect_scenes(vid, threshold)], indent=2)

    @staticmethod
    def _cmd_detect_motion(kwargs: Dict[str, Any]) -> str:
        vid = FilePath(value=kwargs["video"])
        min_area_val = int(kwargs["min_area"])
        min_area = MinArea(value=min_area_val)
        return json.dumps([m.model_dump() for m in VisionAgentOrchestrator.get_video_analysis().detect_motion(vid, min_area)], indent=2)

    @staticmethod
    def _cmd_track(kwargs: Dict[str, Any]) -> str:
        vid = FilePath(value=kwargs["video"])
        x, y, w, h = [int(v) for v in kwargs["bbox"].split(",")]
        bbox = BoundingBox(x=x, y=y, width=w, height=h)
        max_frames_val = int(kwargs["max_frames"])
        max_frames = MaxFrames(value=max_frames_val)
        return json.dumps([b.model_dump() for b in VisionAgentOrchestrator.get_object_tracking().track_object(vid, bbox, max_frames)], indent=2)

    @staticmethod
    def _cmd_timeline(kwargs: Dict[str, Any]) -> str:
        vid = FilePath(value=kwargs["video"])
        interval_val = int(kwargs["interval"])
        interval = IntervalSeconds(value=float(interval_val))
        return json.dumps(asyncio.run(VisionAgentOrchestrator.get_video_timeline().generate_timeline(vid, interval)).model_dump(), indent=2)

    @staticmethod
    def _execute_video_cmd(command: str, kwargs: Dict[str, Any]) -> str | None:
        handlers = {
            "video-info": VisionAgentOrchestrator._cmd_video_info,
            "extract-frames": VisionAgentOrchestrator._cmd_extract_frames,
            "convert": VisionAgentOrchestrator._cmd_convert,
            "check-corruption": VisionAgentOrchestrator._cmd_check_corruption,
            "create-gif": VisionAgentOrchestrator._cmd_create_gif,
            "detect-scenes": VisionAgentOrchestrator._cmd_detect_scenes,
            "detect-motion": VisionAgentOrchestrator._cmd_detect_motion,
            "track": VisionAgentOrchestrator._cmd_track,
            "timeline": VisionAgentOrchestrator._cmd_timeline,
        }
        if command in handlers:
            return handlers[command](kwargs)
        return None

    @staticmethod
    def _execute_memory_cmd(command: str, kwargs: Dict[str, Any]) -> str | None:
        if command == "memory-store":
            img = FilePath(value=kwargs["image"])
            label = MemoryLabel(value=kwargs["label"])
            return json.dumps(VisionAgentOrchestrator.get_visual_memory().remember_image(img, label).model_dump(), indent=2)
        elif command == "memory-search":
            query = FilePath(value=kwargs["query"])
            max_dist_val = int(kwargs["max_distance"])
            max_distance = DistanceThreshold(value=max_dist_val)
            res = VisionAgentOrchestrator.get_visual_memory().find_similar_images(query, max_distance)
            return json.dumps([r.model_dump() for r in res], indent=2)
        elif command == "memory-list":
            import os
            memory_dir = os.path.expanduser("~/.vision-memory")
            index_file = os.path.join(memory_dir, "index.json")
            if os.path.exists(index_file):
                with open(index_file) as f:
                    data = json.load(f)
                return json.dumps(data, indent=2)
            return json.dumps({})
        return None

    @classmethod
    def execute_in_process(cls, command: CommandName, kwargs: dict) -> CommandOutput:
        """Route and execute any command in-process across domains."""
        try:
            cmd_val = command.value if command else ""
            img_res = cls._execute_image_cmd(cmd_val, kwargs)
            if img_res is not None:
                return CommandOutput(value=img_res)

            vid_res = cls._execute_video_cmd(cmd_val, kwargs)
            if vid_res is not None:
                return CommandOutput(value=vid_res)

            mem_res = cls._execute_memory_cmd(cmd_val, kwargs)
            if mem_res is not None:
                return CommandOutput(value=mem_res)

        except Exception as e:
            return CommandOutput(value=json.dumps({"error": str(e)}))

        return CommandOutput(value=json.dumps({"error": f"Unknown command: {command.value if command else ''}"}))
