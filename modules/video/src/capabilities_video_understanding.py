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
from modules.shared.src.taxonomy_vision_models_vo import (
    AnalysisPrompt,
    FilePath,
    FrameAnalysis,
    VideoUnderstanding,
)
from modules.shared.src.utility_opencv_ops import open_video_capture

logger = logging.getLogger("mcp_server.infrastructure.video_understanding")

MAX_KEY_FRAMES = 12
MAX_SUMMARY_CHARS = 12_000

# Locked sampling interval for analyze-video. Kept high so local CPU-only
# VLM backends never attempt to infer hundreds of frames per call.
ANALYZE_VIDEO_INTERVAL = 30.0


class VideoUnderstandingAnalyzer(VideoUnderstandingProtocol):
    """Analyze selected video frames with a vision-language model.

    Frames are selected from scene changes, high-motion events, and uniform
    sampling. The capability bounds the number of VLM requests and removes
    generated frame files when the analysis finishes.
    """

    _taxonomy_marker = VideoUnderstanding

    def __init__(
        self,
        video_analysis: VideoAnalysisProtocol,
        video_processing: VideoProcessingProtocol,
        llm: LLMVisionProtocol,
    ):
        self._video_analysis = video_analysis
        self._video_processing = video_processing
        self._llm = llm

    def analyze(
        self,
        video_path: FilePath,

        prompt: AnalysisPrompt,
        interval: float = 30.0,
        scene_threshold: float = 20.0,
        min_area: int = 500,
        top_motion: int = 5,
    ) -> VideoUnderstanding:
        """Select, analyze, and summarize bounded key-frame samples.

        Sampling interval is locked to ``ANALYZE_VIDEO_INTERVAL`` (30s) so a
        single call never exceeds ``MAX_KEY_FRAMES`` VLM inferences.
        """
        cv2 = self._opencv.cv2
        path = video_path.value

        info = self._video_processing.get_info(video_path)
        fps = info.fps or 30.0
        frame_count = info.frame_count
        target_idx: set[int] = set()

        scenes = self._video_analysis.detect_scenes(
            video_path, SceneThreshold(value=20.0)
        )
        for scene in scenes:
            idx = int(scene.timestamp * fps)
            if 0 <= idx < frame_count:
                target_idx.add(idx)

        events = self._video_analysis.detect_motion(video_path, MinArea(value=500))
        events.sort(key=lambda event: event.magnitude, reverse=True)
        for event in events[:5]:
            idx = int(event.timestamp * fps)
            if 0 <= idx < frame_count:
                target_idx.add(idx)

        interval = ANALYZE_VIDEO_INTERVAL
        step = max(1, int(interval))
        for idx in range(0, frame_count, step):
            target_idx.add(idx)

        selected_indices = sorted(target_idx)
        if len(selected_indices) > MAX_KEY_FRAMES:
            positions = {
                round(index * (len(selected_indices) - 1) / (MAX_KEY_FRAMES - 1))
                for index in range(MAX_KEY_FRAMES)
            }
            selected_indices = [
                selected_indices[position] for position in sorted(positions)
            ]

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
        with tempfile.TemporaryDirectory(prefix="vu_") as out_dir:
            cap: Any = open_video_capture(path)
            extracted: list[tuple[int, str]] = []
            try:
                for idx in selected_indices:
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

            corrupted = self._video_processing.check_corruption(video_path)
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

            summary = self._synthesize_summary(extracted, descriptions)
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
                "scene_changes": len(scenes),
                "motion_events": len(events),
                "uniform_interval": step,
                "key_frames_extracted": extracted_count,
                "max_key_frames": MAX_KEY_FRAMES,
            },
            frames=frame_analyses,
            summary=summary,
        )

    def _synthesize_summary(
        self, extracted: list[tuple[int, str]], descriptions: list[str]
    ) -> str:
        """Generate a bounded summary from per-frame descriptions."""
        if not descriptions:
            return "No frames could be extracted for analysis."

        summary_text = "\n".join(descriptions)
        if len(summary_text) > MAX_SUMMARY_CHARS:
            summary_text = (
                summary_text[:MAX_SUMMARY_CHARS]
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
