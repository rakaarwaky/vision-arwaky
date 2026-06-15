"""Video timeline: generate agent-readable video summaries at intervals."""

import os
import tempfile
from typing import List
from src.shared.video_timeline_protocol import VideoTimelineProtocol
from src.shared.opencv_image_port import OpenCVImagePort
from src.shared.video_processing_protocol import VideoProcessingProtocol
from src.shared.video_analysis_protocol import VideoAnalysisProtocol
from src.shared.vision_models_vo import VideoTimeline, FilePath, IntervalSeconds


class VideoTimelineGenerator(VideoTimelineProtocol):
    """Generate structured timelines summarizing video content over time."""

    def __init__(
        self,
        opencv_port: OpenCVImagePort,
        video_cap: VideoProcessingProtocol,
        analysis_cap: VideoAnalysisProtocol,
    ):
        """Initialize with OpenCVPort, VideoProcessingProtocol and VideoAnalysisProtocol."""
        self._opencv = opencv_port
        self._video_cap = video_cap
        self._analysis_cap = analysis_cap

    async def generate_timeline(self, video_path: FilePath, interval: IntervalSeconds) -> VideoTimeline:
        """Generate a timeline with key frames at regular intervals."""
        cap = self._opencv.get_video_capture(video_path.value)
        if not cap.isOpened():
            return VideoTimeline(
                video_path=video_path.value,
                total_frames=0,
                fps=0.0,
                key_frames=[],
            )

        fps = cap.get(self._opencv.cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(self._opencv.cv2.CAP_PROP_FRAME_COUNT))
        interval_val = interval.value if interval else 5.0
        frame_interval = int(fps * interval_val) if fps > 0 else 30

        key_frames: List[dict] = []
        frame_idx = 0
        tmp_dir = tempfile.mkdtemp(prefix="vision_timeline_")

        while frame_idx < total_frames:
            cap.set(self._opencv.cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = cap.read()
            if not ret:
                break

            # Save key frame thumbnail
            frame_path = os.path.join(tmp_dir, f"frame_{frame_idx:06d}.jpg")
            self._opencv.write_image(frame_path, frame)

            # Compute basic stats
            gray = self._opencv.to_grayscale(frame)
            brightness = float(gray.mean())
            sharpness = float(self._opencv.cv2.Laplacian(gray, self._opencv.cv2.CV_64F).var())

            timestamp = frame_idx / fps if fps > 0 else 0

            key_frames.append({
                "frame_index": frame_idx,
                "timestamp": round(timestamp, 2),
                "path": frame_path,
                "brightness": round(brightness, 2),
                "sharpness": round(sharpness, 2),
            })

            frame_idx += frame_interval

        cap.release()

        return VideoTimeline(
            video_path=video_path.value,
            total_frames=total_frames,
            fps=round(fps, 2),
            key_frames=key_frames,
        )
