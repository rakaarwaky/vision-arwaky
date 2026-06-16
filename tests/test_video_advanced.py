
"""Advanced tests for video processing."""
import os
import tempfile
import json
import numpy as np
import cv2
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


class TestVideoProcessingProcessor:
    def test_get_info(self):
        from src.video.capabilities_video_processing_processor import VideoProcessingProcessor
        from src.opencv.infrastructure_opencv_image_adapter import OpenCVImageAdapter
        from src.video.infrastructure_ffmpeg_video_adapter import FFmpegVideoAdapter
        from src.shared.vision_models_vo import FilePath
        
        proc = VideoProcessingProcessor(OpenCVImageAdapter(), FFmpegVideoAdapter())
        path = create_test_video()
        try:
            info = proc.get_info(FilePath(value=path))
            assert info.frame_count == 10
            assert info.fps == 10.0
        finally:
            os.unlink(path)

    def test_check_corruption(self):
        from src.video.capabilities_video_processing_processor import VideoProcessingProcessor
        from src.opencv.infrastructure_opencv_image_adapter import OpenCVImageAdapter
        from src.video.infrastructure_ffmpeg_video_adapter import FFmpegVideoAdapter
        from src.shared.vision_models_vo import FilePath
        
        proc = VideoProcessingProcessor(OpenCVImageAdapter(), FFmpegVideoAdapter())
        path = create_test_video()
        try:
            assert proc.check_corruption(FilePath(value=path)) is False
        finally:
            os.unlink(path)

    def test_check_corruption_nonexistent(self):
        from src.video.capabilities_video_processing_processor import VideoProcessingProcessor
        from src.opencv.infrastructure_opencv_image_adapter import OpenCVImageAdapter
        from src.video.infrastructure_ffmpeg_video_adapter import FFmpegVideoAdapter
        from src.shared.vision_models_vo import FilePath
        
        proc = VideoProcessingProcessor(OpenCVImageAdapter(), FFmpegVideoAdapter())
        # Non-existent file - corrupted or exception
        try:
            result = proc.check_corruption(FilePath(value="/nonexistent.mp4"))
            assert result is True
        except (RuntimeError, FileNotFoundError, OSError):
            pass


class TestVideoAnalysis:
    def test_detect_scenes(self):
        from src.video.capabilities_video_analysis_analyzer import VideoAnalysisAnalyzer
        from src.opencv.infrastructure_opencv_image_adapter import OpenCVImageAdapter
        from src.shared.vision_models_vo import FilePath, SceneThreshold
        
        proc = VideoAnalysisAnalyzer(OpenCVImageAdapter())
        path = create_test_video(30)
        try:
            scenes = proc.detect_scenes(FilePath(value=path), SceneThreshold(value=30.0))
            assert isinstance(scenes, list)
        finally:
            os.unlink(path)

    def test_detect_motion(self):
        from src.video.capabilities_video_analysis_analyzer import VideoAnalysisAnalyzer
        from src.opencv.infrastructure_opencv_image_adapter import OpenCVImageAdapter
        from src.shared.vision_models_vo import FilePath, MinArea
        
        proc = VideoAnalysisAnalyzer(OpenCVImageAdapter())
        path = create_test_video(30)
        try:
            events = proc.detect_motion(FilePath(value=path), MinArea(value=100))
            assert isinstance(events, list)
        finally:
            os.unlink(path)


class TestVideoOrchestrator:
    def test_execute_video_info(self):
        from src.video.agent_video_orchestrator import VideoOrchestrator
        path = create_test_video()
        try:
            result = VideoOrchestrator.execute_video_cmd("video-info", {"video": path})
            assert result is not None
            data = json.loads(result)
            assert "fps" in data
        finally:
            os.unlink(path)

    def test_execute_video_unknown(self):
        from src.video.agent_video_orchestrator import VideoOrchestrator
        assert VideoOrchestrator.execute_video_cmd("nonexistent", {}) is None

    def test_execute_check_corruption(self):
        from src.video.agent_video_orchestrator import VideoOrchestrator
        path = create_test_video()
        try:
            result = VideoOrchestrator.execute_video_cmd("check-corruption", {"video": path})
            assert result is not None
            data = json.loads(result)
            assert "corrupted" in data
        finally:
            os.unlink(path)

    def test_get_opencv(self):
        from src.video.agent_video_orchestrator import VideoOrchestrator
        ocv = VideoOrchestrator.get_opencv()
        assert ocv is not None


class TestObjectTracking:
    def test_tracker_init(self):
        from src.tracking.capabilities_object_tracking_tracker import ObjectTrackingTracker
        from src.opencv.infrastructure_opencv_image_adapter import OpenCVImageAdapter
        tracker = ObjectTrackingTracker(OpenCVImageAdapter())
        assert tracker is not None
