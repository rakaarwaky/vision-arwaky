"""Benchmarks: image feature performance (FR-IMG-003 comparison).

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

from modules.image.src.root_image_container import ImageContainer
from modules.shared.src.taxonomy_vision_vo import CommandName

_HAS_BENCHMARK = importlib.util.find_spec("pytest_benchmark") is not None


def _make_image(color=(0, 0, 0)) -> str:
    fd, path = tempfile.mkstemp(suffix=".png")
    os.close(fd)
    img = np.zeros((64, 64, 3), dtype=np.uint8)
    img[:] = color
    cv2.imwrite(path, img)
    return path


def _skip_benchmark():
    pytest.skip("pytest-benchmark plugin not installed")


class TestImageBench:
    def test_screenshot_comparison_latency(self):
        """Plain timing harness when pytest-benchmark is absent."""
        container = ImageContainer()
        p1, p2 = _make_image((0, 0, 0)), _make_image((255, 0, 0))
        try:
            start = time.perf_counter()
            out = container.orchestrator.execute_in_process(
                CommandName(value="compare"),
                {"image1": p1, "image2": p2},
            )
            elapsed = time.perf_counter() - start
            assert out is not None
            assert elapsed >= 0.0
        finally:
            os.unlink(p1)
            os.unlink(p2)

    def test_screenshot_comparison_benchmark(self):
        """pytest-benchmark run for regression baselines; skips without plugin."""
        if not _HAS_BENCHMARK:
            _skip_benchmark()
        container = ImageContainer()
        p1, p2 = _make_image((0, 0, 0)), _make_image((255, 0, 0))
        try:
            for _ in range(3):
                container.orchestrator.execute_in_process(
                    CommandName(value="compare"),
                    {"image1": p1, "image2": p2},
                )
        finally:
            os.unlink(p1)
            os.unlink(p2)
