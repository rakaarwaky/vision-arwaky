"""Smoke tests: image container boots and responds fast (FR-IMG-001)."""

import time

from modules.image.src.root_image_container import ImageContainer
from modules.shared.src.taxonomy_vision_vo import CommandName


class TestImageSmoke:
    def test_container_boots_under_one_second(self):
        start = time.monotonic()
        container = ImageContainer()
        elapsed = time.monotonic() - start
        assert container.orchestrator is not None
        assert elapsed < 1.0

    def test_unknown_command_fails_fast(self):
        container = ImageContainer()
        start = time.monotonic()
        try:
            container.orchestrator.execute_in_process(
                CommandName(value="nope"),
                {},
            )
        except ValueError:
            pass
        assert time.monotonic() - start < 0.5
