"""Acceptance tests: business requirements FR-VID-001..005."""

import json
import os
import tempfile

import cv2
import numpy as np

from modules.shared.src.taxonomy_vision_vo import CommandName
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


class TestVideoAcceptance:
    def test_fr_vid_001_video_metadata(self):
        """FR-VID-001: metadata read returns structured record."""
        container = VideoContainer()
        vid = _make_temp_video(num_frames=12)
        try:
            out = container.orchestrator.execute_in_process(
                CommandName(value="video-info"),
                {"video": vid},
            )
            payload = json.loads(out.value)
            assert isinstance(payload, dict)
        finally:
            os.unlink(vid)

    def test_fr_vid_corruption_check(self):
        """FR-VID-00x: corruption check returns a controlled boolean."""
        container = VideoContainer()
        vid = _make_temp_video(num_frames=8)
        try:
            out = container.orchestrator.execute_in_process(
                CommandName(value="check-corruption"),
                {"video": vid},
            )
            payload = json.loads(out.value)
            assert isinstance(payload["corrupted"], bool)
        finally:
            os.unlink(vid)
