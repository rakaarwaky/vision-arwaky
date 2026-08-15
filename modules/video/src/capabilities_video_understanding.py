import logging
import os
import tempfile
from typing import Any

from modules.shared.src.contract_llm_vision_protocol import LLMVisionProtocol
from modules.shared.src.contract_opencv_image_protocol import OpenCVImageProtocol
from modules.shared.src.contract_video_analysis_protocol import (
    MinArea,
    SceneThreshold,
    VideoAnalysisProtocol,
)
from modules.shared.src.contract_video_processing_protocol import (
    VideoProcessingProtocol,
)
from modules.shared.src.contract_video_understanding_protocol import (
    VideoUnderstandingProtocol,
)
from modules.shared.src.taxonomy_vision_models_vo import (
    AnalysisPrompt,
    FilePath,
    FrameAnalysis,
    VideoUnderstanding,
)

logger = logging.getLogger("mcp_server.infrastructure.video_understanding")


class VideoUnderstandingAnalyzer(VideoUnderstandingProtocol):
    """Smart video understanding capability.

    Selects core/key frames using three complementary strategies
    (scene-change, top-motion, uniform sampling), analyzes each selected
    frame with the VLM, then synthesizes a natural-language summary.
    """

    _taxonomy_marker = VideoUnderstanding

    def __init__(
        self,
        video_analysis: VideoAnalysisProtocol,
        video_processing: VideoProcessingProtocol,
        llm: LLMVisionProtocol,
        opencv: OpenCVImageProtocol,
    ):
        self._video_analysis = video_analysis
        self._video_processing = video_processing
        self._llm = llm
        self._opencv = opencv

    def analyze(
        self,
        video_path: FilePath,
        prompt: AnalysisPrompt,
        interval: float = 30.0,
        scene_threshold: float = 20.0,
        min_area: int = 500,
        top_motion: int = 5,
    ) -> VideoUnderstanding:
        cv2 = self._opencv.cv2
        path = video_path.value

        info = self._video_processing.get_info(video_path)
        fps = info.fps or 30.0
        frame_count = info.frame_count

        target_idx: set[int] = set()

        # 1. Scene changes — capture the frame at each transition
        scenes = self._video_analysis.detect_scenes(
            video_path, SceneThreshold(value=scene_threshold)
        )
        for s in scenes:
            idx = int(s.timestamp * fps)
            if 0 <= idx < frame_count:
                target_idx.add(idx)

        # 2. Motion events — capture frames with the highest motion magnitude
        events = self._video_analysis.detect_motion(video_path, MinArea(value=min_area))
        events.sort(key=lambda ev: ev.magnitude, reverse=True)
        for ev in events[:top_motion]:
            idx = int(ev.timestamp * fps)
            if 0 <= idx < frame_count:
                target_idx.add(idx)

        # 3. Uniform sampling — baseline coverage every `interval` frames
        step = max(1, int(interval))
        for idx in range(0, frame_count, step):
            target_idx.add(idx)

        # Extract the selected key frames to a temp directory
        out_dir = tempfile.mkdtemp(prefix="vu_")
        cap: Any = self._opencv.get_video_capture(path)
        extracted: list[tuple[int, str]] = []
        try:
            for idx in sorted(target_idx):
                cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
                ret, frame = cap.read()
                if not ret:
                    continue
                out_path = os.path.join(out_dir, f"frame_{idx:06d}.jpg")
                cv2.imwrite(out_path, frame)
                extracted.append((idx, out_path))
        finally:
            cap.release()

        corrupted = self._video_processing.check_corruption(video_path)

        per_frame_prompt = (
            prompt.value
            if prompt and prompt.value
            else (
                "Describe this video frame in detail. "
                "What objects, people, actions do you see?"
            )
        )

        frame_analyses: list[FrameAnalysis] = []
        descriptions: list[str] = []
        for i, (idx, frame_path) in enumerate(extracted):
            timestamp = round(idx / fps, 1)
            source = "llm"
            try:
                text = self._llm.analyze_image(
                    FilePath(value=frame_path), AnalysisPrompt(value=per_frame_prompt)
                )
            except (RuntimeError, ValueError, OSError) as e:
                text = f"(VLM unavailable: {e})"
                source = "fallback"
            frame_analyses.append(
                FrameAnalysis(
                    frame=i + 1,
                    timestamp_s=timestamp,
                    source=source,
                    description=text,
                )
            )
            descriptions.append(f"[{timestamp}s] {text[:200]}")

        summary = self._synthesize_summary(extracted, descriptions)

        return VideoUnderstanding(
            video={
                "path": path,
                "resolution": f"{info.width}x{info.height}",
                "fps": round(fps, 1),
                "total_frames": frame_count,
                "duration_s": round(frame_count / fps, 1) if fps else 0,
                "corrupted": corrupted,
            },
            sampling={
                "scene_changes": len(scenes),
                "motion_events": len(events),
                "uniform_interval": step,
                "key_frames_extracted": len(extracted),
            },
            frames=frame_analyses,
            summary=summary,
        )

    def _synthesize_summary(
        self, extracted: list[tuple[int, str]], descriptions: list[str]
    ) -> str:
        if not descriptions:
            return "No frames could be extracted for analysis."

        summary_prompt = (
            "Based on these frame-by-frame descriptions, write a brief video "
            "summary (3-5 sentences) covering what happens, the setting, people "
            "involved, and key actions:\n\n" + "\n".join(descriptions)
        )
        # Use the first key frame as visual context for the synthesis call.
        first_frame = FilePath(value=extracted[0][1])
        try:
            return self._llm.analyze_image(
                first_frame, AnalysisPrompt(value=summary_prompt)
            )
        except (RuntimeError, ValueError, OSError) as e:
            logger.warning(f"Summary synthesis failed, falling back to join: {e}")
            return " ".join(descriptions)
