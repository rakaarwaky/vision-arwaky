
"""Advanced memory tests."""
import os
import tempfile
import numpy as np
import cv2


def create_test_image():
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    cv2.rectangle(img, (20, 20), (80, 80), (255, 255, 255), -1)
    return img


class TestMemoryOrchestrator:
    def test_get_visual_memory(self):
        from src.memory.agent_memory_orchestrator import MemoryOrchestrator
        mem = MemoryOrchestrator.get_visual_memory()
        assert mem is not None

    def test_execute_memory_store(self):
        from src.memory.agent_memory_orchestrator import MemoryOrchestrator
        img = create_test_image()
        fd, path = tempfile.mkstemp(suffix=".png")
        os.close(fd)
        cv2.imwrite(path, img)
        try:
            result = MemoryOrchestrator.execute_memory_cmd("memory-store", {"image": path, "label": "test"})
            assert result is not None
        finally:
            os.unlink(path)

    def test_execute_memory_search(self):
        from src.memory.agent_memory_orchestrator import MemoryOrchestrator
        img = create_test_image()
        fd, path = tempfile.mkstemp(suffix=".png")
        os.close(fd)
        cv2.imwrite(path, img)
        try:
            result = MemoryOrchestrator.execute_memory_cmd("memory-search", {"query": path, "max_distance": 0})
            assert result is not None
        finally:
            os.unlink(path)

    def test_execute_memory_list(self):
        from src.memory.agent_memory_orchestrator import MemoryOrchestrator
        result = MemoryOrchestrator.execute_memory_cmd("memory-list", {})
        assert result is not None

    def test_execute_memory_unknown(self):
        from src.memory.agent_memory_orchestrator import MemoryOrchestrator
        assert MemoryOrchestrator.execute_memory_cmd("nonexistent", {}) is None


class TestVisualMemoryStore:
    def test_remember_and_find(self):
        from src.memory.capabilities_visual_memory_store import VisualMemoryStore
        from src.opencv.infrastructure_opencv_image_adapter import OpenCVImageAdapter
        from src.system_utils.infrastructure_system_utils_util import SystemUtilsUtil
        from src.shared.vision_models_vo import FilePath, MemoryLabel, DistanceThreshold
        
        store = VisualMemoryStore(OpenCVImageAdapter(), SystemUtilsUtil())
        img = create_test_image()
        fd, path = tempfile.mkstemp(suffix=".png")
        os.close(fd)
        cv2.imwrite(path, img)
        try:
            entry = store.remember_image(FilePath(value=path), MemoryLabel(value="test_label"))
            assert entry.label == "test_label"
            assert entry.phash != ""
            
            results = store.find_similar_images(FilePath(value=path), DistanceThreshold(value=5))
            assert len(results) >= 1
        finally:
            os.unlink(path)

    def test_remember_nonexistent(self):
        from src.memory.capabilities_visual_memory_store import VisualMemoryStore
        from src.opencv.infrastructure_opencv_image_adapter import OpenCVImageAdapter
        from src.system_utils.infrastructure_system_utils_util import SystemUtilsUtil
        from src.shared.vision_models_vo import FilePath, MemoryLabel
        import pytest
        
        store = VisualMemoryStore(OpenCVImageAdapter(), SystemUtilsUtil())
        with pytest.raises((FileNotFoundError, PermissionError)):
            store.remember_image(FilePath(value="/nonexistent.png"), MemoryLabel(value="test"))

    def test_hamming_distance(self):
        from src.memory.capabilities_visual_memory_store import VisualMemoryStore
        d = VisualMemoryStore._hamming_distance("1010", "1011")
        assert d == 1
        d = VisualMemoryStore._hamming_distance("1010", "0101")
        assert d == 4


class TestSystemUtils:
    def test_system_utils_init(self):
        from src.system_utils.infrastructure_system_utils_util import SystemUtilsUtil
        utils = SystemUtilsUtil()
        assert utils is not None
        assert hasattr(utils, "FFMPEG_PATH")

    def test_opencv_adapter_properties(self):
        from src.opencv.infrastructure_opencv_image_adapter import OpenCVImageAdapter
        adapter = OpenCVImageAdapter()
        assert adapter.cv2 is not None
        assert adapter.np is not None

    def test_opencv_read_image(self):
        from src.opencv.infrastructure_opencv_image_adapter import OpenCVImageAdapter
        adapter = OpenCVImageAdapter()
        result = adapter.read_image("nonexistent.png")
        assert result is None

    def test_opencv_dimensions(self):
        from src.opencv.infrastructure_opencv_image_adapter import OpenCVImageAdapter
        import numpy as np
        adapter = OpenCVImageAdapter()
        img = np.zeros((50, 100, 3), dtype=np.uint8)
        w, h = adapter.get_dimensions(img)
        assert w == 100
        assert h == 50

    def test_opencv_grayscale(self):
        from src.opencv.infrastructure_opencv_image_adapter import OpenCVImageAdapter
        import numpy as np
        adapter = OpenCVImageAdapter()
        gray = adapter.to_grayscale(np.zeros((10, 10, 3), dtype=np.uint8))
        assert len(gray.shape) == 2

    def test_opencv_edges_and_contours(self):
        from src.opencv.infrastructure_opencv_image_adapter import OpenCVImageAdapter
        import numpy as np
        adapter = OpenCVImageAdapter()
        gray = np.zeros((100, 100), dtype=np.uint8)
        gray[30:70, 30:70] = 255
        edges = adapter.detect_edges(gray, 50, 150)
        contours = adapter.find_contours(edges)
        assert len(contours) >= 1
        area = adapter.get_contour_area(contours[0])
        assert area > 0
        x, y, w, h = adapter.get_bounding_box(contours[0])
        assert w > 0
        assert h > 0

    def test_opencv_abs_diff(self):
        from src.opencv.infrastructure_opencv_image_adapter import OpenCVImageAdapter
        import numpy as np
        adapter = OpenCVImageAdapter()
        i1 = np.zeros((10, 10, 3), dtype=np.uint8)
        i2 = np.ones((10, 10, 3), dtype=np.uint8) * 255
        diff = adapter.abs_diff(i1, i2)
        assert diff.sum() > 0

    def test_opencv_phash(self):
        from src.opencv.infrastructure_opencv_image_adapter import OpenCVImageAdapter
        import numpy as np
        adapter = OpenCVImageAdapter()
        img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        h = adapter.compute_phash(img)
        assert h is not None
        assert len(h) > 0
