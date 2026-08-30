"""Unit tests for shared OpenCV utility functions."""

import os
import tempfile
from typing import Any

import cv2
import numpy as np

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


def _make_temp_video(num_frames=20, width=100, height=100) -> str:
    fd, path = tempfile.mkstemp(suffix=".mp4")
    os.close(fd)
    cv2_any: Any = cv2
    writer = cv2.VideoWriter(
        path, cv2_any.VideoWriter_fourcc(*"mp4v"), 10, (width, height)
    )
    for i in range(num_frames):
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        frame[:] = (200, 0, 0) if i < 10 else (0, 200, 0)
        writer.write(frame)
    writer.release()
    return path


class TestReadWriteImage:
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


class TestGrayscaleAndAbsDiff:
    def test_grayscale_and_abs_diff(self):
        img1 = np.zeros((50, 50, 3), dtype=np.uint8)
        img2 = np.ones((50, 50, 3), dtype=np.uint8) * 100
        diff = compute_abs_diff(img1, img2)
        gray = to_grayscale(diff)
        assert gray.shape == (50, 50)
        assert np.all(gray == 100)


class TestPhashComputation:
    def test_phash_computation(self):
        img1 = np.zeros((64, 64, 3), dtype=np.uint8)
        img2 = np.zeros((64, 64, 3), dtype=np.uint8)
        cv2.rectangle(img2, (10, 10), (50, 50), (255, 255, 255), -1)

        hash1 = compute_phash(img1)
        hash2 = compute_phash(img2)
        assert isinstance(hash1, str) and len(hash1) > 0
        assert isinstance(hash2, str) and len(hash2) > 0
        assert hash1 != hash2


class TestContourAndBoundingBox:
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
