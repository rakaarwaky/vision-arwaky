"""Advanced tests for video processing."""

import json
import os
import tempfile

import cv2
import numpy as np
import pytest


def create_test_video(num_frames=10):
    fd, path = tempfile.mkstemp(suffix=".mp4")
    os.close(fd)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(path, fourcc, 10, (100, 100))
    for i in range(num_frames):
        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        frame[:] = (i * 25 % 255, 0, 0)
        out.write(frame)
    out.release()
    return path


class FakeLLM:
    def __init__(self):
        self.calls = []

    def analyze_image(self, image_path, prompt, timeout=120):
        self.calls.append((image_path.value, prompt.value, timeout))
        return "A test frame description."


def make_video_orchestrator():
    """Build a VideoOrchestrator with injected ports (DI)."""
    from modules.opencv.src.capabilities_opencv_image_adapter import (
        OpenCVImageAdapter,
    )
    from modules.video.src.agent_video_orchestrator import VideoOrchestrator
    from modules.video.src.capabilities_ffmpeg_adapter import FFmpegVideoAdapter
    from modules.video.src.capabilities_object_tracker import ObjectTrackingTracker
    from modules.video.src.capabilities_timeline_generator import (
        VideoTimelineGenerator,
    )
    from modules.video.src.capabilities_video_analyzer import VideoAnalysisAnalyzer
    from modules.video.src.capabilities_video_processor import (
        VideoProcessingProcessor,
    )
    from modules.video.src.capabilities_video_understanding import (
        VideoUnderstandingAnalyzer,
    )

    opencv = OpenCVImageAdapter()
    ffmpeg = FFmpegVideoAdapter()
    video_proc = VideoProcessingProcessor(opencv, ffmpeg)
    video_analysis = VideoAnalysisAnalyzer(opencv)
    video_timeline = VideoTimelineGenerator(opencv, video_proc, video_analysis)
    object_tracking = ObjectTrackingTracker(opencv)
    video_understanding = VideoUnderstandingAnalyzer(
        video_analysis=video_analysis,
        video_processing=video_proc,
        llm=FakeLLM(),
        opencv=opencv,
    )
    return VideoOrchestrator(
        video_processing=video_proc,
        video_analysis=video_analysis,
        video_timeline=video_timeline,
        object_tracking=object_tracking,
        opencv=opencv,
        ffmpeg=ffmpeg,
        video_understanding=video_understanding,
    )


class TestVideoProcessingProcessor:
    def test_get_info(self):
        from modules.opencv.src.capabilities_opencv_image_adapter import (
            OpenCVImageAdapter,
        )
        from modules.shared.src.taxonomy_vision_models_vo import FilePath
        from modules.video.src.capabilities_ffmpeg_adapter import FFmpegVideoAdapter
        from modules.video.src.capabilities_video_processor import (
            VideoProcessingProcessor,
        )

        proc = VideoProcessingProcessor(OpenCVImageAdapter(), FFmpegVideoAdapter())
        path = create_test_video()
        try:
            info = proc.get_info(FilePath(value=path))
            assert info.frame_count == 10
            assert info.fps == 10.0
        finally:
            os.unlink(path)

    def test_check_corruption(self):
        from modules.opencv.src.capabilities_opencv_image_adapter import (
            OpenCVImageAdapter,
        )
        from modules.shared.src.taxonomy_vision_models_vo import FilePath
        from modules.video.src.capabilities_ffmpeg_adapter import FFmpegVideoAdapter
        from modules.video.src.capabilities_video_processor import (
            VideoProcessingProcessor,
        )

        proc = VideoProcessingProcessor(OpenCVImageAdapter(), FFmpegVideoAdapter())
        path = create_test_video()
        try:
            assert proc.check_corruption(FilePath(value=path)) is False
        finally:
            os.unlink(path)

    def test_check_corruption_nonexistent(self):
        from modules.opencv.src.capabilities_opencv_image_adapter import (
            OpenCVImageAdapter,
        )
        from modules.shared.src.taxonomy_vision_models_vo import FilePath
        from modules.video.src.capabilities_ffmpeg_adapter import FFmpegVideoAdapter
        from modules.video.src.capabilities_video_processor import (
            VideoProcessingProcessor,
        )

        proc = VideoProcessingProcessor(OpenCVImageAdapter(), FFmpegVideoAdapter())
        # Non-existent file - corrupted or exception
        try:
            result = proc.check_corruption(FilePath(value="/nonexistent.mp4"))
            assert result is True
        except (RuntimeError, FileNotFoundError, OSError):
            pass


class TestVideoAnalysis:
    def test_detect_scenes(self):
        from modules.opencv.src.capabilities_opencv_image_adapter import (
            OpenCVImageAdapter,
        )
        from modules.shared.src.taxonomy_vision_models_vo import (
            FilePath,
            SceneThreshold,
        )
        from modules.video.src.capabilities_video_analyzer import VideoAnalysisAnalyzer

        proc = VideoAnalysisAnalyzer(OpenCVImageAdapter())
        path = create_test_video(30)
        try:
            scenes = proc.detect_scenes(
                FilePath(value=path), SceneThreshold(value=30.0)
            )
            assert isinstance(scenes, list)
        finally:
            os.unlink(path)

    def test_detect_motion(self):
        from modules.opencv.src.capabilities_opencv_image_adapter import (
            OpenCVImageAdapter,
        )
        from modules.shared.src.taxonomy_vision_models_vo import FilePath, MinArea
        from modules.video.src.capabilities_video_analyzer import VideoAnalysisAnalyzer

        proc = VideoAnalysisAnalyzer(OpenCVImageAdapter())
        path = create_test_video(30)
        try:
            events = proc.detect_motion(FilePath(value=path), MinArea(value=100))
            assert isinstance(events, list)
        finally:
            os.unlink(path)


class TestVideoOrchestrator:
    def test_execute_video_info(self):
        from modules.shared.src.taxonomy_vision_models_vo import CommandName

        orch = make_video_orchestrator()
        path = create_test_video()
        try:
            result = orch.execute_in_process(
                CommandName(value="video-info"), {"video": path}
            )
            assert result is not None
            data = json.loads(result.value)
            assert "fps" in data
        finally:
            os.unlink(path)

    def test_execute_video_unknown(self):
        from modules.shared.src.taxonomy_vision_models_vo import CommandName

        orch = make_video_orchestrator()
        with pytest.raises(ValueError):
            orch.execute_in_process(CommandName(value="nonexistent"), {})

    def test_execute_check_corruption(self):
        from modules.shared.src.taxonomy_vision_models_vo import CommandName

        orch = make_video_orchestrator()
        path = create_test_video()
        try:
            result = orch.execute_in_process(
                CommandName(value="check-corruption"), {"video": path}
            )
            assert result is not None
            data = json.loads(result.value)
            assert "corrupted" in data
        finally:
            os.unlink(path)

    def test_orchestrator_ports(self):
        orch = make_video_orchestrator()
        assert orch._opencv is not None
        assert orch._ffmpeg is not None
        assert orch._video_processing is not None
        assert orch._video_analysis is not None
        assert orch._video_timeline is not None
        assert orch._object_tracking is not None
        assert orch._video_understanding is not None


class TestVideoUnderstanding:
    def test_analyze_video_returns_bounded_structured_result(self):
        from modules.opencv.src.capabilities_opencv_image_adapter import (
            OpenCVImageAdapter,
        )
        from modules.shared.src.taxonomy_vision_models_vo import (
            AnalysisPrompt,
            FilePath,
        )
        from modules.video.src.capabilities_ffmpeg_adapter import FFmpegVideoAdapter
        from modules.video.src.capabilities_video_analyzer import VideoAnalysisAnalyzer
        from modules.video.src.capabilities_video_processor import (
            VideoProcessingProcessor,
        )
        from modules.video.src.capabilities_video_understanding import (
            MAX_KEY_FRAMES,
            VideoUnderstandingAnalyzer,
        )

        opencv = OpenCVImageAdapter()
        video_proc = VideoProcessingProcessor(opencv, FFmpegVideoAdapter())
        video_analysis = VideoAnalysisAnalyzer(opencv)
        fake_llm = FakeLLM()
        capability = VideoUnderstandingAnalyzer(
            video_analysis=video_analysis,
            video_processing=video_proc,
            llm=fake_llm,
            opencv=opencv,
        )
        path = create_test_video(140)
        try:
            result = capability.analyze(
                FilePath(value=path),
                AnalysisPrompt(value="Describe the frame."),
                interval=1,
            )
            assert result.frames
            assert len(result.frames) == MAX_KEY_FRAMES
            assert result.sampling["max_key_frames"] == MAX_KEY_FRAMES
            assert len(fake_llm.calls) == len(result.frames) + 1
            assert result.summary == "A test frame description."
            assert all(not os.path.exists(call[0]) for call in fake_llm.calls)
        finally:
            os.unlink(path)


class TestObjectTracking:
    def test_tracker_init(self):
        from modules.opencv.src.capabilities_opencv_image_adapter import (
            OpenCVImageAdapter,
        )
        from modules.video.src.capabilities_object_tracker import ObjectTrackingTracker

        tracker = ObjectTrackingTracker(OpenCVImageAdapter())
        assert tracker is not None
