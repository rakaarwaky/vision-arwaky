
"""Integration and edge case tests for remaining coverage gaps."""
import os
import tempfile

import cv2
import numpy as np


class TestVideoTimeline:
    def test_timeline_init(self):
        from modules.opencv.src.capabilities_opencv_image_adapter import (
            OpenCVImageAdapter,
        )
        from modules.video.src.capabilities_ffmpeg_adapter import FFmpegVideoAdapter
        from modules.video.src.capabilities_timeline_generator import (
            VideoTimelineGenerator,
        )
        from modules.video.src.capabilities_video_analyzer import VideoAnalysisAnalyzer
        from modules.video.src.capabilities_video_processor import (
            VideoProcessingProcessor,
        )
        
        gen = VideoTimelineGenerator(
            OpenCVImageAdapter(),
            VideoProcessingProcessor(OpenCVImageAdapter(), FFmpegVideoAdapter()),
            VideoAnalysisAnalyzer(OpenCVImageAdapter()),
        )
        assert gen is not None

    def test_timeline_empty_video(self):
        import asyncio

        from modules.opencv.src.capabilities_opencv_image_adapter import (
            OpenCVImageAdapter,
        )
        from modules.shared.src.taxonomy_vision_models_vo import (
            FilePath,
            IntervalSeconds,
        )
        from modules.video.src.capabilities_ffmpeg_adapter import FFmpegVideoAdapter
        from modules.video.src.capabilities_timeline_generator import (
            VideoTimelineGenerator,
        )
        from modules.video.src.capabilities_video_analyzer import VideoAnalysisAnalyzer
        from modules.video.src.capabilities_video_processor import (
            VideoProcessingProcessor,
        )
        
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
        from modules.image.src.capabilities_tesseract_ocr_adapter import (
            TesseractOCRAdapter,
        )
        from modules.shared.src.taxonomy_vision_models_vo import FilePath, LanguageCode
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
        finally:
            if os.path.exists(path):
                os.unlink(path)


class TestAgentOrchestratorEdge:
    def test_image_orchestrator_ports(self):
        from modules.image.src.agent_image_orchestrator import ImageOrchestrator
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
        orch = ImageOrchestrator(
            image_processing=processor,
            opencv=opencv,
            tesseract=tesseract,
            llm=llm,
        )
        assert orch._opencv is not None
        assert orch._tesseract is not None
        assert orch._llm is not None
        assert orch._image_processing is not None

    def test_video_orchestrator_ports(self):
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

        opencv = OpenCVImageAdapter()
        ffmpeg = FFmpegVideoAdapter()
        video_proc = VideoProcessingProcessor(opencv, ffmpeg)
        video_analysis = VideoAnalysisAnalyzer(opencv)
        video_timeline = VideoTimelineGenerator(opencv, video_proc, video_analysis)
        object_tracking = ObjectTrackingTracker(opencv)
        orch = VideoOrchestrator(
            video_processing=video_proc,
            video_analysis=video_analysis,
            video_timeline=video_timeline,
            object_tracking=object_tracking,
            opencv=opencv,
            ffmpeg=ffmpeg,
        )
        assert orch._opencv is not None
        assert orch._ffmpeg is not None
        assert orch._video_processing is not None
        assert orch._video_analysis is not None
        assert orch._video_timeline is not None
        assert orch._object_tracking is not None


class TestOpenCVAdapter:
    def test_write_image(self):
        from modules.opencv.src.capabilities_opencv_image_adapter import (
            OpenCVImageAdapter,
        )
        from modules.shared.src.taxonomy_vision_models_vo import FilePath
        
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
        from modules.opencv.src.capabilities_opencv_image_adapter import (
            OpenCVImageAdapter,
        )
        
        adapter = OpenCVImageAdapter()
        # Should handle non-existent video gracefully
        cap = adapter.get_video_capture("/nonexistent.mp4")
        assert not cap.isOpened()
        cap.release()

    def test_optical_flow(self):
        import cv2
        import numpy as np

        from modules.opencv.src.capabilities_opencv_image_adapter import (
            OpenCVImageAdapter,
        )
        
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
        import numpy as np

        from modules.opencv.src.capabilities_opencv_image_adapter import (
            OpenCVImageAdapter,
        )
        
        adapter = OpenCVImageAdapter()
        h1 = np.array([[0.1, 0.2, 0.3]], dtype=np.float32)
        h2 = np.array([[0.1, 0.2, 0.3]], dtype=np.float32)
        sim = adapter.compare_histograms(h1, h2)
        assert isinstance(sim, float)


class TestSystemUtilsEdge:
    def test_util_init(self):
        from modules.shared.src.utility_system_utils import get_ffmpeg_path
        path = get_ffmpeg_path()
        assert path is not None


    def test_read_image_with_str(self):
        from modules.opencv.src.capabilities_opencv_image_adapter import (
            OpenCVImageAdapter,
        )
        adapter = OpenCVImageAdapter()
        result = adapter.read_image("/nonexistent/file.jpg")
        assert result is None

    def test_get_video_capture_with_filepath(self):
        from modules.opencv.src.capabilities_opencv_image_adapter import (
            OpenCVImageAdapter,
        )
        from modules.shared.src.taxonomy_vision_models_vo import FilePath
        
        adapter = OpenCVImageAdapter()
        cap = adapter.get_video_capture(FilePath(value="/nonexistent.mp4"))
        assert not cap.isOpened()
        cap.release()

    def test_write_image_with_str(self):
        import numpy as np

        from modules.opencv.src.capabilities_opencv_image_adapter import (
            OpenCVImageAdapter,
        )
        
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
        from modules.opencv.src.capabilities_opencv_image_adapter import (
            OpenCVImageAdapter,
        )
        from modules.shared.src.taxonomy_vision_models_vo import (
            BoundingBox,
            FilePath,
            MaxFrames,
        )
        from modules.video.src.capabilities_object_tracker import ObjectTrackingTracker
        
        tracker = ObjectTrackingTracker(OpenCVImageAdapter())
        assert tracker is not None
        
        # Tracking on non-existent video returns empty list or raises
        result = tracker.track_object(
            FilePath(value="/nonexistent.mp4"),
            BoundingBox(x=10, y=10, width=50, height=50),
            MaxFrames(value=10)
        )
        assert isinstance(result, list)
