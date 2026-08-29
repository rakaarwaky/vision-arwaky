"""Unit tests for video domain OpenCV algorithms."""

import os
import tempfile
from typing import Any

import cv2
import numpy as np

from modules.shared.src.taxonomy_vision_vo import (
    FilePath,
    MinArea,
    SceneThreshold,
)
from modules.shared.src.utility_opencv_ops import (
    calc_optical_flow,
    check_video_corruption,
    get_video_metadata,
)
from modules.video.src.capabilities_video_analyzer import VideoAnalysisAnalyzer


def _make_temp_video(num_frames=20, width=100, height=100) -> str:
    fd, path = tempfile.mkstemp(suffix=".mp4")
    os.close(fd)
    cv2_any: Any = cv2
    writer = cv2.VideoWriter(
        path, cv2_any.VideoWriter_fourcc(*"mp4v"), 10, (width, height)
    )
    for i in range(num_frames):
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        frame[:] = (200, 0, 0) if i < 10 else (0, 200, 0)
        writer.write(frame)
    writer.release()
    return path


class TestVideoCVOperations:
    def test_video_metadata_and_corruption(self):
        vid_path = _make_temp_video(num_frames=15, width=120, height=80)
        try:
            info = get_video_metadata(FilePath(value=vid_path))
            assert info.frame_count == 15
            assert info.fps == 10.0
            assert info.width == 120
            assert info.height == 80

            corrupted = check_video_corruption(FilePath(value=vid_path))
            assert corrupted is False
        finally:
            os.unlink(vid_path)

    def test_scene_detection(self):
        vid_path = _make_temp_video(num_frames=20)
        analyzer = VideoAnalysisAnalyzer()
        try:
            scenes = analyzer.detect_scenes(
                FilePath(value=vid_path), SceneThreshold(value=20.0)
            )
            assert len(scenes) >= 1
            assert scenes[0].timestamp.value > 0.0

        finally:
            os.unlink(vid_path)

    def test_motion_detection(self):
        vid_path = _make_temp_video(num_frames=20)
        analyzer = VideoAnalysisAnalyzer()
        try:
            events = analyzer.detect_motion(FilePath(value=vid_path), MinArea(value=50))
            assert len(events) >= 1
            assert events[0].region is not None
            assert events[0].region.width > 0
        finally:
            os.unlink(vid_path)

    def test_optical_flow(self):
        prev = np.ones((80, 80), dtype=np.uint8) * 50
        nxt = np.ones((80, 80), dtype=np.uint8) * 50
        prev[20:50, 20:50] = 200
        nxt[25:55, 25:55] = 200
        flow = calc_optical_flow(prev, nxt)
        assert flow is not None
        assert flow.shape == (80, 80, 2)
