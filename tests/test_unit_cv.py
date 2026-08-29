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
from modules.shared.src.taxonomy_vision_models_vo import (
    FilePath,
    MinArea,
    SceneThreshold,
)
from modules.shared.src.utility_opencv_ops import (
    calc_optical_flow,
    check_video_corruption,
    compare_histograms,
    compute_abs_diff,
    compute_phash,
    find_contours,
    get_bounding_box,
    get_contour_area,
    get_video_metadata,
    read_image,
    to_grayscale,
    write_image,
)
from modules.video.src.capabilities_video_analyzer import VideoAnalysisAnalyzer


def _make_temp_image(width=100, height=100, color=(255, 0, 0)) -> tuple[str, np.ndarray]:
    fd, path = tempfile.mkstemp(suffix=".png")
    os.close(fd)
    img = np.zeros((height, width, 3), dtype=np.uint8)
    img[:] = color
    cv2.imwrite(path, img)
    return path, img


def _make_temp_video(num_frames=20, width=100, height=100) -> str:
    fd, path = tempfile.mkstemp(suffix=".mp4")
    os.close(fd)
    writer = cv2.VideoWriter(path, cv2.VideoWriter_fourcc(*"mp4v"), 10, (width, height))
    for i in range(num_frames):
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        frame[:] = (200, 0, 0) if i < 10 else (0, 200, 0)
        writer.write(frame)
    writer.release()
    return path


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


class TestVideoCVOperations:
    def test_video_metadata_and_corruption(self):
        vid_path = _make_temp_video(num_frames=15, width=120, height=80)
        try:
            info = get_video_metadata(FilePath(value=vid_path))
            assert info.frame_count == 15
            assert info.fps == 10.0
            assert info.width == 120
            assert info.height == 80

            corrupted = check_video_corruption(FilePath(value=vid_path))
            assert corrupted is False
        finally:
            os.unlink(vid_path)

    def test_scene_detection(self):
        vid_path = _make_temp_video(num_frames=20)
        analyzer = VideoAnalysisAnalyzer()
        try:
            scenes = analyzer.detect_scenes(
                FilePath(value=vid_path), SceneThreshold(value=20.0)
            )
            assert len(scenes) >= 1
            assert scenes[0].timestamp > 0.0
        finally:
            os.unlink(vid_path)

    def test_motion_detection(self):
        vid_path = _make_temp_video(num_frames=20)
        analyzer = VideoAnalysisAnalyzer()
        try:
            events = analyzer.detect_motion(
                FilePath(value=vid_path), MinArea(value=50)
            )
            assert len(events) >= 1
            assert events[0].region.width > 0
        finally:
            os.unlink(vid_path)

    def test_optical_flow(self):
        prev = np.ones((80, 80), dtype=np.uint8) * 50
        nxt = np.ones((80, 80), dtype=np.uint8) * 50
        prev[20:50, 20:50] = 200
        nxt[25:55, 25:55] = 200

        flow = calc_optical_flow(prev, nxt)
        assert flow.shape == (80, 80, 2)
        assert np.any(np.abs(flow) > 0)
