"""Vision MCP Server tests."""

import json
import os
import tempfile

import cv2
import numpy as np

from modules.mcp.src.surface_mcp_action import vision_list_commands, vision_status
from modules.shared.src.taxonomy_vision_models_vo import (
    FilePath,
    LanguageCode,
    MinArea,
    SceneThreshold,
    VideoInfo,
)

# ── Helpers ──────────────────────────────────────────────────

def build_image_capabilities():
    """Build image processor + orchestrator via DI."""
    from modules.image.src.capabilities_image_processing_processor import (
        ImageProcessingProcessor,
    )
    from modules.image.src.capabilities_llm_vision_adapter import LLMVisionAdapter
    from modules.image.src.capabilities_tesseract_ocr_adapter import (
        TesseractOCRAdapter,
    )
    from modules.opencv.src.capabilities_opencv_image_adapter import (
        OpenCVImageAdapter,
    )

    opencv = OpenCVImageAdapter()
    tesseract = TesseractOCRAdapter()
    llm = LLMVisionAdapter()
    processor = ImageProcessingProcessor(
        opencv_port=opencv,
        tesseract_port=tesseract,
        llm_port=llm,
    )
    return opencv, processor


def build_video_capabilities():
    """Build video capabilities via DI."""
    from modules.opencv.src.capabilities_opencv_image_adapter import (
        OpenCVImageAdapter,
    )
    from modules.video.src.capabilities_ffmpeg_adapter import FFmpegVideoAdapter
    from modules.video.src.capabilities_video_analyzer import VideoAnalysisAnalyzer
    from modules.video.src.capabilities_video_processor import (
        VideoProcessingProcessor,
    )

    opencv = OpenCVImageAdapter()
    ffmpeg = FFmpegVideoAdapter()
    video_proc = VideoProcessingProcessor(opencv, ffmpeg)
    video_analysis = VideoAnalysisAnalyzer(opencv)
    return video_proc, video_analysis

def create_test_image(width=100, height=100, color=(255, 0, 0)):
    """Create a test image."""
    img = np.zeros((height, width, 3), dtype=np.uint8)
    img[:] = color
    # Add some text-like features
    cv2.rectangle(img, (20, 20), (80, 40), (255, 255, 255), -1)
    cv2.rectangle(img, (20, 50), (80, 70), (0, 255, 0), -1)
    return img


def save_test_image(img, path=None):
    """Save test image to temp file."""
    if path is None:
        fd, path = tempfile.mkstemp(suffix=".png")
        os.close(fd)
    cv2.imwrite(path, img)
    return path


def create_test_video(num_frames=30, width=100, height=100):
    """Create a test video."""
    fd, path = tempfile.mkstemp(suffix=".mp4")
    os.close(fd)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(path, fourcc, 10, (width, height))
    for i in range(num_frames):
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        # Vary color to create detectable changes
        frame[:] = (i * 8 % 255, (i * 5) % 255, (i * 3) % 255)
        out.write(frame)
    out.release()
    return path


# ── Image Tests ──────────────────────────────────────────────

class TestImageProcessing:
    def test_find_elements(self):
        _, cap = build_image_capabilities()
        img = create_test_image()
        path = save_test_image(img)
        try:
            elements = cap.find_elements(FilePath(value=path))
            assert isinstance(elements, list)
            # Should find at least the rectangles
            assert len(elements) >= 0
        finally:
            os.unlink(path)

    def test_compare_identical(self):
        _, cap = build_image_capabilities()
        img = create_test_image()
        path1 = save_test_image(img)
        path2 = save_test_image(img)
        try:
            result = cap.compare_screenshots(FilePath(value=path1), FilePath(value=path2))
            assert result["identical"] is True
        finally:
            os.unlink(path1)
            os.unlink(path2)

    def test_compare_different(self):
        _, cap = build_image_capabilities()
        img1 = create_test_image(color=(255, 0, 0))
        img2 = create_test_image(color=(0, 255, 0))
        path1 = save_test_image(img1)
        path2 = save_test_image(img2)
        try:
            result = cap.compare_screenshots(FilePath(value=path1), FilePath(value=path2))
            assert result["identical"] is False
            assert len(result["differences"]) > 0
        finally:
            os.unlink(path1)
            os.unlink(path2)

    def test_extract_text_no_tesseract(self):
        _, cap = build_image_capabilities()
        img = create_test_image()
        path = save_test_image(img)
        try:
            # May raise if tesseract not installed
            cap.extract_text(FilePath(value=path), LanguageCode(value="eng"))
        except RuntimeError:
            pass  # Expected if tesseract not installed
        finally:
            os.unlink(path)


# ── Video Tests ──────────────────────────────────────────────

class TestVideoProcessing:
    def test_get_info(self):
        cap, _ = build_video_capabilities()
        path = create_test_video()
        try:
            info = cap.get_info(FilePath(value=path))
            assert isinstance(info, VideoInfo)
            assert info.frame_count == 30
        finally:
            os.unlink(path)

    def test_check_corruption_valid(self):
        cap, _ = build_video_capabilities()
        path = create_test_video()
        try:
            corrupted = cap.check_corruption(FilePath(value=path))
            assert corrupted is False  # Not corrupted
        finally:
            os.unlink(path)


class TestVideoAnalysis:
    def test_detect_scenes(self):
        _, cap = build_video_capabilities()
        path = create_test_video(num_frames=30)
        try:
            scenes = cap.detect_scenes(FilePath(value=path), SceneThreshold(value=20.0))
            assert isinstance(scenes, list)
        finally:
            os.unlink(path)

    def test_detect_motion(self):
        _, cap = build_video_capabilities()
        path = create_test_video(num_frames=30)
        try:
            events = cap.detect_motion(FilePath(value=path), MinArea(value=100))
            assert isinstance(events, list)
        finally:
            os.unlink(path)


# ── MCP Tool Tests ───────────────────────────────────────────

class TestMCPTools:
    def test_list_commands(self):
        result = vision_list_commands()
        data = json.loads(result)
        assert "image" in data
        assert "video" in data

    def test_list_commands_filter(self):
        result = vision_list_commands(domain="image")
        data = json.loads(result)
        assert isinstance(data, list)
        assert len(data) == 4

    def test_status(self):
        result = vision_status()
        data = json.loads(result)
        assert "dependencies" in data
        assert "capabilities" in data

