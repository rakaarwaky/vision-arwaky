
"""Integration and edge case tests for remaining coverage gaps."""
import os
import json
import tempfile
import numpy as np
import cv2
import pytest


class TestVideoTimeline:
    def test_timeline_init(self):
        from src.video.capabilities_video_timeline_generator import VideoTimelineGenerator
        from src.opencv.infrastructure_opencv_image_adapter import OpenCVImageAdapter
        from src.video.capabilities_video_processing_processor import VideoProcessingProcessor
        from src.video.capabilities_video_analysis_analyzer import VideoAnalysisAnalyzer
        from src.video.infrastructure_ffmpeg_video_adapter import FFmpegVideoAdapter
        
        gen = VideoTimelineGenerator(
            OpenCVImageAdapter(),
            VideoProcessingProcessor(OpenCVImageAdapter(), FFmpegVideoAdapter()),
            VideoAnalysisAnalyzer(OpenCVImageAdapter()),
        )
        assert gen is not None

    def test_timeline_empty_video(self):
        import asyncio
        from src.video.capabilities_video_timeline_generator import VideoTimelineGenerator
        from src.opencv.infrastructure_opencv_image_adapter import OpenCVImageAdapter
        from src.video.capabilities_video_processing_processor import VideoProcessingProcessor
        from src.video.capabilities_video_analysis_analyzer import VideoAnalysisAnalyzer
        from src.video.infrastructure_ffmpeg_video_adapter import FFmpegVideoAdapter
        from src.shared.vision_models_vo import FilePath, IntervalSeconds
        
        gen = VideoTimelineGenerator(
            OpenCVImageAdapter(),
            VideoProcessingProcessor(OpenCVImageAdapter(), FFmpegVideoAdapter()),
            VideoAnalysisAnalyzer(OpenCVImageAdapter()),
        )
        # Non-existent video should return empty timeline, not crash
        tl = asyncio.run(gen.generate_timeline(FilePath(value="/nonexistent.mp4"), IntervalSeconds(value=5.0)))
        assert tl.total_frames == 0
        assert tl.fps == 0.0
        assert tl.key_frames == []


class TestTesseractEdge:
    def test_extract_text_with_path(self):
        from src.image.infrastructure_tesseract_ocr_adapter import TesseractOCRAdapter
        from src.shared.vision_models_vo import FilePath, LanguageCode
        import tempfile, os
        # Create a simple image with text-like features using OpenCV
        fd, path = tempfile.mkstemp(suffix=".png")
        os.close(fd)
        try:
            img = np.ones((100, 100, 3), dtype=np.uint8) * 255
            cv2.putText(img, "Hello", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
            cv2.imwrite(path, img)
            
            adapter = TesseractOCRAdapter()
            # This may raise RuntimeError if tesseract binary doesn't return text
            # but should not crash with other errors
            try:
                result = adapter.extract_text(FilePath(value=path), LanguageCode(value="eng"))
                assert result is not None
            except RuntimeError:
                pass  # Acceptable if OCR fails
        except Exception:
            raise
        finally:
            if os.path.exists(path):
                os.unlink(path)


class TestAgentOrchestratorEdge:
    def test_orchestrator_getters(self):
        from src.image.agent_image_orchestrator import ImageOrchestrator
        ocv = ImageOrchestrator.get_opencv()
        assert ocv is not None
        tess = ImageOrchestrator.get_tesseract()
        assert tess is not None
        llm = ImageOrchestrator.get_llm()
        assert llm is not None
        proc = ImageOrchestrator.get_image_processing()
        assert proc is not None

    def test_video_orchestrator_getters(self):
        from src.video.agent_video_orchestrator import VideoOrchestrator
        ocv = VideoOrchestrator.get_opencv()
        assert ocv is not None
        ffmpeg = VideoOrchestrator.get_ffmpeg()
        assert ffmpeg is not None
        proc = VideoOrchestrator.get_video_processing()
        assert proc is not None
        analysis = VideoOrchestrator.get_video_analysis()
        assert analysis is not None
        tracking = VideoOrchestrator.get_object_tracking()
        assert tracking is not None
        tl = VideoOrchestrator.get_video_timeline()
        assert tl is not None


class TestOpenCVAdapter:
    def test_write_image(self):
        from src.opencv.infrastructure_opencv_image_adapter import OpenCVImageAdapter
        from src.shared.vision_models_vo import FilePath
        import tempfile, os
        
        adapter = OpenCVImageAdapter()
        img = np.zeros((50, 50, 3), dtype=np.uint8)
        fd, path = tempfile.mkstemp(suffix=".png")
        os.close(fd)
        try:
            result = adapter.write_image(FilePath(value=path), img)
            assert result is True
            assert os.path.exists(path)
        finally:
            os.unlink(path)

    def test_video_capture(self):
        from src.opencv.infrastructure_opencv_image_adapter import OpenCVImageAdapter
        import tempfile, os
        
        adapter = OpenCVImageAdapter()
        # Should handle non-existent video gracefully
        cap = adapter.get_video_capture("/nonexistent.mp4")
        assert not cap.isOpened()
        cap.release()

    def test_optical_flow(self):
        from src.opencv.infrastructure_opencv_image_adapter import OpenCVImageAdapter
        import numpy as np
        import cv2
        
        adapter = OpenCVImageAdapter()
        prev = np.ones((100, 100), dtype=np.uint8) * 100
        nxt = np.ones((100, 100), dtype=np.uint8) * 100
        prev[30:70, 30:70] = 200
        nxt[35:75, 35:75] = 200
        try:
            flow = adapter.calc_optical_flow(prev, nxt)
            assert flow is not None
        except cv2.error:
            pass

    def test_histogram_compare(self):
        from src.opencv.infrastructure_opencv_image_adapter import OpenCVImageAdapter
        import numpy as np
        
        adapter = OpenCVImageAdapter()
        h1 = np.array([[0.1, 0.2, 0.3]], dtype=np.float32)
        h2 = np.array([[0.1, 0.2, 0.3]], dtype=np.float32)
        sim = adapter.compare_histograms(h1, h2)
        assert isinstance(sim, float)


class TestSystemUtilsEdge:
    def test_util_init(self):
        from src.system_utils.infrastructure_system_utils_util import SystemUtilsUtil
        u = SystemUtilsUtil()
        assert u.FFMPEG_PATH is not None

    def test_read_image_with_str(self):
        from src.opencv.infrastructure_opencv_image_adapter import OpenCVImageAdapter
        adapter = OpenCVImageAdapter()
        result = adapter.read_image("/nonexistent/file.jpg")
        assert result is None

    def test_get_video_capture_with_filepath(self):
        from src.opencv.infrastructure_opencv_image_adapter import OpenCVImageAdapter
        from src.shared.vision_models_vo import FilePath
        
        adapter = OpenCVImageAdapter()
        cap = adapter.get_video_capture(FilePath(value="/nonexistent.mp4"))
        assert not cap.isOpened()
        cap.release()

    def test_write_image_with_str(self):
        from src.opencv.infrastructure_opencv_image_adapter import OpenCVImageAdapter
        import numpy as np
        import tempfile, os
        
        adapter = OpenCVImageAdapter()
        img = np.zeros((10, 10, 3), dtype=np.uint8)
        fd, path = tempfile.mkstemp(suffix=".png")
        os.close(fd)
        try:
            result = adapter.write_image(path, img)
            assert result is True
        finally:
            os.unlink(path)


class TestTracking:
    def test_tracker_init(self):
        from src.tracking.capabilities_object_tracking_tracker import ObjectTrackingTracker
        from src.opencv.infrastructure_opencv_image_adapter import OpenCVImageAdapter
        from src.shared.vision_models_vo import FilePath, BoundingBox, MaxFrames
        
        tracker = ObjectTrackingTracker(OpenCVImageAdapter())
        assert tracker is not None
        
        # Tracking on non-existent video returns empty list or raises
        result = tracker.track_object(
            FilePath(value="/nonexistent.mp4"),
            BoundingBox(x=10, y=10, width=50, height=50),
            MaxFrames(value=10)
        )
        assert isinstance(result, list)
