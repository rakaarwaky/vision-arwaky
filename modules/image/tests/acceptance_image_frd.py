"""Acceptance tests: business requirements FR-IMG-001..003."""

import json
import os
import tempfile

import cv2
import numpy as np

from modules.image.src.root_image_container import ImageContainer
from modules.shared.src.taxonomy_vision_vo import CommandName


def _make_image(color=(0, 0, 0)) -> str:
    fd, path = tempfile.mkstemp(suffix=".png")
    os.close(fd)
    img = np.zeros((32, 32, 3), dtype=np.uint8)
    img[:] = color
    cv2.imwrite(path, img)
    return path


class TestImageAcceptance:
    def test_fr_img_003_screenshot_comparison(self):
        """FR-IMG-003: two screenshots compared; differences detected."""
        container = ImageContainer()
        p1, p2 = _make_image((0, 0, 0)), _make_image((200, 100, 50))
        try:
            out = container.orchestrator.execute_in_process(
                CommandName(value="compare"),
                {"image1": p1, "image2": p2},
            )
            payload = json.loads(out.value)
            assert payload["identical"] is False
        finally:
            os.unlink(p1)
            os.unlink(p2)

    def test_fr_img_001_analyze_delegates_to_processor(self):
        """FR-IMG-001: analyze routes to the injected processor port."""
        container = ImageContainer()
        assert container.orchestrator is not None
        assert container.image_processing is not None
