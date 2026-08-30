"""Unit tests for deterministic OpenCV operations and computer vision algorithms."""

import os
import tempfile

import cv2
import numpy as np

from modules.image.src.capabilities_image_processing_processor import (
    ImageProcessingProcessor,
)
from modules.image.src.capabilities_llm_vision_adapter import LLMVisionAdapter
from modules.image.src.capabilities_tesseract_ocr_adapter import (
    TesseractOCRAdapter,
)
from modules.shared.src.taxonomy_vision_vo import (
    FilePath,
)
from modules.shared.src.utility_opencv_ops import (
    compute_abs_diff,
    compute_phash,
    find_contours,
    get_bounding_box,
    get_contour_area,
    read_image,
    to_grayscale,
    write_image,
)


def _make_temp_image(
    width=100, height=100, color=(255, 0, 0)
) -> tuple[str, np.ndarray]:
    fd, path = tempfile.mkstemp(suffix=".png")
    os.close(fd)
    img = np.zeros((height, width, 3), dtype=np.uint8)
    img[:] = color
    cv2.imwrite(path, img)
    return path, img


class TestImageCVOperations:
    def test_read_and_write_image(self):
        path, img = _make_temp_image()
        try:
            loaded = read_image(path)
            assert loaded is not None
            assert loaded.shape == img.shape

            out_fd, out_path = tempfile.mkstemp(suffix=".png")
            os.close(out_fd)
            try:
                assert write_image(out_path, loaded) is True
                assert os.path.exists(out_path)
            finally:
                os.unlink(out_path)
        finally:
            os.unlink(path)

    def test_grayscale_and_abs_diff(self):
        img1 = np.zeros((50, 50, 3), dtype=np.uint8)
        img2 = np.ones((50, 50, 3), dtype=np.uint8) * 100
        diff = compute_abs_diff(img1, img2)
        gray = to_grayscale(diff)
        assert gray.shape == (50, 50)
        assert np.all(gray == 100)

    def test_phash_computation(self):
        img1 = np.zeros((64, 64, 3), dtype=np.uint8)
        img2 = np.zeros((64, 64, 3), dtype=np.uint8)
        cv2.rectangle(img2, (10, 10), (50, 50), (255, 255, 255), -1)

        hash1 = compute_phash(img1)
        hash2 = compute_phash(img2)
        assert isinstance(hash1, str) and len(hash1) > 0
        assert isinstance(hash2, str) and len(hash2) > 0
        assert hash1 != hash2

    def test_contour_and_bounding_box(self):
        mask = np.zeros((100, 100), dtype=np.uint8)
        cv2.rectangle(mask, (20, 30), (60, 80), 255, -1)

        contours = find_contours(mask)
        assert len(contours) == 1
        area = get_contour_area(contours[0])
        assert area > 1500
        bbox = get_bounding_box(contours[0])
        assert bbox.x == 20
        assert bbox.y == 30
        assert bbox.width == 41
        assert bbox.height == 51

    def test_screenshot_comparison_identical(self):
        p1, _ = _make_temp_image(color=(128, 128, 128))
        p2, _ = _make_temp_image(color=(128, 128, 128))
        proc = ImageProcessingProcessor(
            tesseract_port=TesseractOCRAdapter(),
            llm_port=LLMVisionAdapter(),
        )
        try:
            comp = proc.compare_screenshots(FilePath(value=p1), FilePath(value=p2))
            assert comp.identical is True
            assert len(comp.differences) == 0
        finally:
            os.unlink(p1)
            os.unlink(p2)

    def test_screenshot_comparison_different(self):
        p1, _ = _make_temp_image(color=(255, 0, 0))
        p2, _ = _make_temp_image(color=(0, 255, 0))
        proc = ImageProcessingProcessor(
            tesseract_port=TesseractOCRAdapter(),
            llm_port=LLMVisionAdapter(),
        )
        try:
            comp = proc.compare_screenshots(FilePath(value=p1), FilePath(value=p2))
            assert comp.identical is False
            assert len(comp.differences) > 0
        finally:
            os.unlink(p1)
            os.unlink(p2)
