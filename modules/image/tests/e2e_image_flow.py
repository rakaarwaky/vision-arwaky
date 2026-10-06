"""E2E tests: full image request lifecycle through orchestrator."""

import json
import os
import tempfile

import cv2
import numpy as np

from modules.image.src.root_image_container import ImageContainer
from modules.shared.src.taxonomy_vision_vo import (
    AnalysisPrompt,
    CommandName,
    FilePath,
    LanguageCode,
)
from modules.shared.src.utility_opencv_ops import read_image


def _make_image(color=(10, 20, 30)) -> str:
    fd, path = tempfile.mkstemp(suffix=".png")
    os.close(fd)
    img = np.zeros((48, 64, 3), dtype=np.uint8)
    img[:] = color
    cv2.imwrite(path, img)
    return path


class TestImageE2E:
    def test_compare_lifecycle(self):
        container = ImageContainer()
        p1, p2 = _make_image((0, 0, 0)), _make_image((255, 255, 255))
        try:
            out = container.orchestrator.execute_in_process(
                CommandName(value="compare"),
                {"image1": p1, "image2": p2},
            )
            payload = json.loads(out.value)
            assert payload["identical"] is False
            assert read_image(p1) is not None
        finally:
            os.unlink(p1)
            os.unlink(p2)

    def test_unknown_command_is_controlled_error(self):
        container = ImageContainer()
        try:
            container.orchestrator.execute_in_process(CommandName(value="bogus"), {})
            assert False, "expected controlled ValueError"
        except ValueError:
            pass
        assert (
            isinstance(AnalysisPrompt(value="x"), AnalysisPrompt)
            and isinstance(LanguageCode(value="eng"), LanguageCode)
            and isinstance(FilePath(value="."), FilePath)
        )
