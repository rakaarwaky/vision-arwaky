"""Smart video understanding capability.

Selects bounded key frames via scene-change, motion, and uniform sampling,
analyzes each with a vision-language model, then synthesizes a summary.
"""

import logging
import os
import tempfile
from typing import Any

import cv2

from modules.shared.src.contract_llm_vision_protocol import LLMVisionProtocol
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
from modules.shared.src.taxonomy_vision_constant import (
    DEFAULT_VIDEO_FPS,
    MAX_SMART_VIDEO_FRAMES,
    MAX_SUMMARY_PROMPT_CHARS,
)
from modules.shared.src.taxonomy_vision_vo import (
    AnalysisPrompt,
    FilePath,
    FrameAnalysis,
    VideoUnderstanding,
    VideoUnderstandingConfig,
)
from modules.shared.src.utility_opencv_ops import open_video_capture

logger = logging.getLogger("mcp_server.infrastructure.video_understanding")


class VideoUnderstandingAnalyzer(VideoUnderstandingProtocol):
    """Analyze selected video frames with a vision-language model.

    Frames are selected from scene changes, high-motion events, and uniform
    sampling. The capability bounds the number of VLM requests and removes
    generated frame files when the analysis finishes.
    """

    def __init__(
        self,
        video_analysis: VideoAnalysisProtocol,
        video_processing: VideoProcessingProtocol,
        llm: LLMVisionProtocol,
    ):
        """Wire the analysis, processing, and vision-language dependencies."""
        self._video_analysis = video_analysis
        self._video_processing = video_processing
        self._llm = llm

    def analyze(
        self,
        video_path: FilePath,
        prompt: AnalysisPrompt,
        config: VideoUnderstandingConfig | None = None,
    ) -> VideoUnderstanding:
        """Select, analyze, and summarize bounded key-frame samples.

        Sampling interval is locked so a single call never exceeds
        ``MAX_SMART_VIDEO_FRAMES`` VLM inferences.
        """
        config = config or VideoUnderstandingConfig()
        path = video_path.value

        info = self._video_processing.get_info(video_path)
        fps = info.fps or DEFAULT_VIDEO_FPS
        frame_count = info.frame_count

        indices, scene_count, motion_count, step = self._select_frame_indices(
            video_path, fps, frame_count, config
        )

        per_frame_prompt = self._build_per_frame_prompt(prompt)

        corrupted = self._video_processing.check_corruption(video_path)
        with tempfile.TemporaryDirectory(prefix="vu_") as out_dir:
            extracted = self._extract_frames(path, fps, indices, out_dir)
            frame_analyses, descriptions = self._analyze_frames(
                extracted, fps, per_frame_prompt
            )
            summary = self.synthesize_summary(extracted, descriptions)
            extracted_count = len(extracted)

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
                "scene_changes": scene_count,
                "motion_events": motion_count,
                "uniform_interval": step,
                "key_frames_extracted": extracted_count,
                "max_key_frames": MAX_SMART_VIDEO_FRAMES,
            },
            frames=frame_analyses,
            summary=summary,
        )

    def _select_frame_indices(
        self,
        video_path: FilePath,
        fps: float,
        frame_count: int,
        config: VideoUnderstandingConfig,
    ) -> tuple[list[int], int, int, int]:
        """Pick representative frame indices bounded by ``MAX_SMART_VIDEO_FRAMES``."""
        target_idx: set[int] = set()

        scenes = self._video_analysis.detect_scenes(
            video_path, SceneThreshold(value=config.scene_threshold)
        )
        for scene in scenes:
            idx = int(scene.timestamp.value * fps)
            if 0 <= idx < frame_count:
                target_idx.add(idx)

        events = self._video_analysis.detect_motion(
            video_path, MinArea(value=config.min_area)
        )
        events.sort(key=lambda event: event.magnitude.value, reverse=True)
        for event in events[: config.top_motion]:
            idx = int(event.timestamp.value * fps)
            if 0 <= idx < frame_count:
                target_idx.add(idx)

        step = max(1, int(config.interval))
        target_idx.update(range(0, frame_count, step))

        indices = sorted(target_idx)
        if len(indices) > MAX_SMART_VIDEO_FRAMES:
            positions = {
                round(index * (len(indices) - 1) / (MAX_SMART_VIDEO_FRAMES - 1))
                for index in range(MAX_SMART_VIDEO_FRAMES)
            }
            indices = [indices[position] for position in sorted(positions)]

        return indices, len(scenes), len(events), step

    @staticmethod
    def _build_per_frame_prompt(prompt: AnalysisPrompt) -> str:
        """Return the per-frame prompt or a sensible default when absent."""
        if prompt and prompt.value:
            return prompt.value
        return (
            "Describe this video frame in detail. "
            "What objects, people, actions do you see?"
        )

    def _extract_frames(
        self,
        path: str,
        fps: float,
        indices: list[int],
        out_dir: str,
    ) -> list[tuple[int, str]]:
        """Decode and persist the selected frames to temporary files."""
        extracted: list[tuple[int, str]] = []
        cap: Any = open_video_capture(path)
        try:
            for idx in indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
                ret, frame = cap.read()
                if not ret:
                    continue
                out_path = os.path.join(out_dir, f"frame_{idx:06d}.jpg")
                if not cv2.imwrite(out_path, frame):
                    logger.warning("Failed to write sampled frame %s", out_path)
                    continue
                extracted.append((idx, out_path))
        finally:
            cap.release()
        return extracted

    def _analyze_frames(
        self,
        extracted: list[tuple[int, str]],
        fps: float,
        per_frame_prompt: str,
    ) -> tuple[list[FrameAnalysis], list[str]]:
        """Run the VLM over each extracted frame, falling back on failure."""
        frame_analyses: list[FrameAnalysis] = []
        descriptions: list[str] = []
        for frame_number, (idx, frame_path) in enumerate(extracted, start=1):
            timestamp = round(idx / fps, 1)
            source = "llm"
            try:
                text = self._llm.analyze_image(
                    FilePath(value=frame_path),
                    AnalysisPrompt(value=per_frame_prompt),
                )
            except (RuntimeError, ValueError, OSError) as error:
                text = f"(VLM unavailable: {error})"
                source = "fallback"
            frame_analyses.append(
                FrameAnalysis(
                    frame=frame_number,
                    timestamp_s=timestamp,
                    source=source,
                    description=text,
                )
            )
            descriptions.append(f"[{timestamp}s] {text[:200]}")
        return frame_analyses, descriptions

    def synthesize_summary(
        self, extracted: list[tuple[int, str]], descriptions: list[str]
    ) -> str:
        """Generate a bounded summary from per-frame descriptions."""
        if not descriptions:
            return "No frames could be extracted for analysis."

        summary_text = "\n".join(descriptions)
        if len(summary_text) > MAX_SUMMARY_PROMPT_CHARS:
            summary_text = (
                summary_text[:MAX_SUMMARY_PROMPT_CHARS]
                + "\n[Additional frame descriptions omitted from summary prompt.]"
            )
        summary_prompt = (
            "Based on these frame-by-frame descriptions, write a brief video "
            "summary (3-5 sentences) covering what happens, the setting, people "
            "involved, and key actions:\n\n" + summary_text
        )
        first_frame = FilePath(value=extracted[0][1])
        try:
            return self._llm.analyze_image(
                first_frame, AnalysisPrompt(value=summary_prompt)
            )
        except (RuntimeError, ValueError, OSError) as error:
            logger.warning("Summary synthesis failed, falling back to join: %s", error)
            return " ".join(descriptions)
