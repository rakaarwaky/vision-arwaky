"""Smoke tests: video container boots and responds fast (FR-VID-001)."""

import json
import time

from modules.shared.src.taxonomy_vision_vo import CommandName
from modules.video.src.root_video_container import VideoContainer


class TestVideoSmoke:
    def test_container_boots_under_one_second(self):
        start = time.monotonic()
        container = VideoContainer()
        elapsed = time.monotonic() - start
        assert container.orchestrator is not None
        assert elapsed < 1.0

    def test_corruption_check_responds_fast(self):
        container = VideoContainer()
        start = time.monotonic()
        out = container.orchestrator.execute_in_process(
            CommandName(value="check-corruption"),
            {"video": "/nonexistent/vision-arwaky-smoke.mp4"},
        )
        payload = json.loads(out.value)
        assert "corrupted" in payload
        assert time.monotonic() - start < 0.5
