"""E2E tests: full video request lifecycle through the orchestrator."""

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


class TestVideoE2E:
    def test_video_info_lifecycle(self):
        container = VideoContainer()
        vid = _make_temp_video()
        try:
            out = container.orchestrator.execute_in_process(
                CommandName(value="video-info"),
                {"video": vid},
            )
            payload = json.loads(out.value)
            assert payload is not None
        finally:
            os.unlink(vid)

    def test_unknown_command_is_controlled_error(self):
        container = VideoContainer()
        try:
            container.orchestrator.execute_in_process(CommandName(value="bogus"), {})
            assert False, "expected controlled ValueError"
        except ValueError:
            pass
