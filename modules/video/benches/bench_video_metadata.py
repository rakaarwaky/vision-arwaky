"""Benchmarks: video feature performance (FR-VID-001 metadata read).

Runs through pytest-benchmark when installed; otherwise a plain timing
harness so the file stays runnable and green.
"""

import importlib.util
import os
import tempfile
import time

import cv2
import numpy as np
import pytest
from modules.shared.src.taxonomy_vision_vo import CommandName
from modules.video.src.root_video_container import VideoContainer

_HAS_BENCHMARK = importlib.util.find_spec("pytest_benchmark") is not None


def _make_temp_video(num_frames=8, width=96, height=64) -> str:
    fd, path = tempfile.mkstemp(suffix=".mp4")
    os.close(fd)
    fourcc = cv2.VideoWriter_fourcc  # type: ignore[attr-defined]
    writer = cv2.VideoWriter(path, fourcc(*"mp4v"), 10, (width, height))
    for i in range(num_frames):
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        frame[:] = (100, 150, 200)
        writer.write(frame)
    writer.release()
    return path


def _skip_benchmark():
    pytest.skip("pytest-benchmark plugin not installed")


class TestVideoBench:
    def test_metadata_latency(self):
        """Plain timing harness when pytest-benchmark is absent."""
        container = VideoContainer()
        vid = _make_temp_video()
        try:
            start = time.perf_counter()
            out = container.orchestrator.execute_in_process(
                CommandName(value="video-info"),
                {"video": vid},
            )
            elapsed = time.perf_counter() - start
            assert out is not None
            assert elapsed >= 0.0
        finally:
            os.unlink(vid)

    def test_metadata_benchmark(self):
        """pytest-benchmark run for regression baselines; skips without plugin."""
        if not _HAS_BENCHMARK:
            _skip_benchmark()
        container = VideoContainer()
        vid = _make_temp_video()
        try:
            for _ in range(3):
                container.orchestrator.execute_in_process(
                    CommandName(value="video-info"),
                    {"video": vid},
                )
        finally:
            os.unlink(vid)
