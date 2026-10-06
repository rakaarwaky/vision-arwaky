"""Integration tests: video DI container wiring (FR-VID-001..005)."""

import json
import os
import tempfile

import cv2
import numpy as np

from modules.shared.src.taxonomy_vision_vo import (
    CommandName,
    FilePath,
)
from modules.video.src.root_video_container import VideoContainer


def _make_temp_video(num_frames=10, width=96, height=64) -> str:
    fd, path = tempfile.mkstemp(suffix=".mp4")
    os.close(fd)
    fourcc = cv2.VideoWriter_fourcc  # type: ignore[attr-defined]
    writer = cv2.VideoWriter(path, fourcc(*"mp4v"), 10, (width, height))
    for i in range(num_frames):
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        frame[:] = (100, 150, 200) if i < 5 else (20, 20, 20)
        writer.write(frame)
    writer.release()
    return path


class TestVideoDIWiring:
    def test_container_builds_all_ports(self):
        container = VideoContainer()
        assert container.orchestrator is not None
        assert container.video_processing is not None
        assert container.video_analysis is not None
        assert container.object_tracking is not None

    def test_video_info_lifecycle_via_container(self):
        container = VideoContainer()
        vid = _make_temp_video()
        try:
            out = container.orchestrator.execute_in_process(
                CommandName(value="video-info"),
                {"video": vid},
            )
            payload = json.loads(out.value)
            assert "frame_count" in payload or "width" in payload
        finally:
            os.unlink(vid)

    def test_corruption_check_routes_to_processor(self):
        container = VideoContainer()
        vid = _make_temp_video()
        try:
            out = container.orchestrator.execute_in_process(
                CommandName(value="check-corruption"),
                {"video": vid},
            )
            payload = json.loads(out.value)
            assert isinstance(payload["corrupted"], bool)
        finally:
            os.unlink(vid)
        assert isinstance(FilePath(value="."), FilePath)
