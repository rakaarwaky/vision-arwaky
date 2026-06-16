"""Tests for shared/contract layer — all protocols, ports, and models."""
import json
import os
import tempfile
import numpy as np
import cv2
from pathlib import Path
from src.shared.vision_models_vo import (
    BoundingBox, Detection, MotionEvent, SceneChange, MemoryEntry,
    VideoTimeline, VisionAnalysis, FilePath, LanguageCode, OcrText,
    CommandName, CommandOutput, MemoryLabel, DistanceThreshold,
    SceneThreshold, MinArea, AnalysisPrompt, IntervalSeconds,
    MaxFrames, TimeSegment, VideoInfo,
)


class TestVisionModels:
    def test_bounding_box(self):
        b = BoundingBox(x=10, y=20, width=100, height=200)
        assert b.x == 10
        assert b.y == 20
        assert b.width == 100
        assert b.height == 200
        d = b.model_dump()
        assert d["x"] == 10

    def test_detection(self):
        d = Detection(label="button", confidence=0.95, bbox=BoundingBox(x=0, y=0, width=50, height=50))
        assert d.label == "button"
        assert d.confidence == 0.95

    def test_video_info(self):
        v = VideoInfo(fps=30.0, frame_count=100, width=1920, height=1080)
        assert v.fps == 30.0
        assert v.frame_count == 100

    def test_vision_analysis(self):
        va = VisionAnalysis(source="llm", text="test", elements=[])
        assert va.source == "llm"
        assert va.text == "test"
        assert va.error is None
        va2 = VisionAnalysis(source="opencv", text="", error="fail")
        assert va2.error == "fail"

    def test_command_name_output(self):
        cn = CommandName(value="analyze")
        assert cn.value == "analyze"
        co = CommandOutput(value='{"ok": true}')
        assert json.loads(co.value)["ok"] is True

    def test_value_objects(self):
        assert LanguageCode(value="eng").value == "eng"
        assert FilePath(value="/tmp/test.png").value == "/tmp/test.png"
        assert MemoryLabel(value="test").value == "test"
        assert DistanceThreshold(value=10).value == 10
        assert SceneThreshold(value=30.0).value == 30.0
        assert MinArea(value=500).value == 500
        assert IntervalSeconds(value=1.0).value == 1.0
        assert MaxFrames(value=300).value == 300
        assert AnalysisPrompt(value="desc").value == "desc"
        assert OcrText(value="hello").value == "hello"
        assert TimeSegment(start=0.0, duration=5.0).start == 0.0
        assert TimeSegment(start=None, duration=None).start is None


class TestProtocolInstantiation:
    """Test that protocols/ports can be subclassed and used."""

    def test_opencv_port_interface(self):
        from src.shared.opencv_image_port import OpenCVImagePort
        assert callable(OpenCVImagePort.read_image)

    def test_image_processing_protocol(self):
        from src.shared.image_processing_protocol import ImageProcessingProtocol
        assert callable(ImageProcessingProtocol.analyze_screenshot)

    def test_llm_vision_port(self):
        from src.shared.llm_vision_port import LLMVisionPort
        assert callable(LLMVisionPort.analyze_image)

    def test_video_processing_protocol(self):
        from src.shared.video_processing_protocol import VideoProcessingProtocol
        assert callable(VideoProcessingProtocol.extract_frames)

    def test_visual_memory_protocol(self):
        from src.shared.visual_memory_protocol import VisualMemoryProtocol
        assert callable(VisualMemoryProtocol.remember_image)
