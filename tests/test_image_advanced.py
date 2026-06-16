
"""Advanced tests for image processing — orchestrator, LLM adapter, tesseract."""
import os
import tempfile
import json
import numpy as np
import cv2
import pytest


def create_test_image(width=200, height=200):
    img = np.zeros((height, width, 3), dtype=np.uint8)
    cv2.rectangle(img, (30, 30), (170, 170), (255, 255, 255), -1)
    cv2.putText(img, "TEST", (50, 120), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)
    return img


def save_test_image(img):
    fd, path = tempfile.mkstemp(suffix=".png")
    os.close(fd)
    cv2.imwrite(path, img)
    return path


class TestImageOrchestrator:
    def test_get_image_processing(self):
        from src.image.agent_image_orchestrator import ImageOrchestrator
        proc = ImageOrchestrator.get_image_processing()
        assert proc is not None
        img = create_test_image()
        path = save_test_image(img)
        try:
            from src.shared.vision_models_vo import FilePath
            elements = proc.find_elements(FilePath(value=path))
            assert isinstance(elements, list)
        finally:
            os.unlink(path)

    def test_execute_image_cmd_analyze_no_llm(self):
        from src.image.agent_image_orchestrator import ImageOrchestrator
        img = create_test_image()
        path = save_test_image(img)
        try:
            result = ImageOrchestrator.execute_image_cmd("analyze", {"image": path})
            assert result is not None
            data = json.loads(result)
            assert "source" in data
        finally:
            os.unlink(path)

    def test_execute_image_cmd_ocr(self):
        from src.image.agent_image_orchestrator import ImageOrchestrator
        img = create_test_image()
        path = save_test_image(img)
        try:
            result = ImageOrchestrator.execute_image_cmd("ocr", {"image": path, "lang": "eng"})
            assert result is not None
        finally:
            os.unlink(path)

    def test_execute_image_cmd_elements(self):
        from src.image.agent_image_orchestrator import ImageOrchestrator
        img = create_test_image()
        path = save_test_image(img)
        try:
            result = ImageOrchestrator.execute_image_cmd("elements", {"image": path})
            assert result is not None
            data = json.loads(result)
            assert isinstance(data, list)
        finally:
            os.unlink(path)

    def test_execute_image_cmd_compare(self):
        from src.image.agent_image_orchestrator import ImageOrchestrator
        img = create_test_image()
        p1 = save_test_image(img)
        p2 = save_test_image(img)
        try:
            result = ImageOrchestrator.execute_image_cmd("compare", {"image1": p1, "image2": p2})
            assert result is not None
            data = json.loads(result)
            assert "identical" in data
        finally:
            os.unlink(p1)
            os.unlink(p2)

    def test_execute_image_cmd_unknown(self):
        from src.image.agent_image_orchestrator import ImageOrchestrator
        assert ImageOrchestrator.execute_image_cmd("nonexistent", {}) is None

    def test_get_opencv(self):
        from src.image.agent_image_orchestrator import ImageOrchestrator
        ocv = ImageOrchestrator.get_opencv()
        assert ocv is not None
        img = ocv.read_image("nonexistent.png")
        assert img is None

    def test_get_tesseract(self):
        from src.image.agent_image_orchestrator import ImageOrchestrator
        tess = ImageOrchestrator.get_tesseract()
        assert tess is not None

    def test_get_llm(self):
        from src.image.agent_image_orchestrator import ImageOrchestrator
        llm = ImageOrchestrator.get_llm()
        assert llm is not None
        assert hasattr(llm, "analyze_image")


class TestLLMVisionAdapter:
    def test_adapter_properties(self):
        from src.image.agent_image_orchestrator import ImageOrchestrator
        adapter = ImageOrchestrator.get_llm()
        assert adapter.config is not None
        assert isinstance(adapter.backend, str)
        assert adapter.model is not None

    def test_adapter_find_free_port(self):
        from src.image.infrastructure_llm_vision_adapter import LLMVisionAdapter
        port = LLMVisionAdapter._find_free_port()
        assert isinstance(port, int)
        assert port > 0
        assert port < 65536

    def test_adapter_bundled_path(self):
        from src.image.infrastructure_llm_vision_adapter import LLMVisionAdapter
        path = LLMVisionAdapter._get_bundled_server_path(LLMVisionAdapter)
        assert path is None or path.exists()


class TestTesseractAdapter:
    def test_extract_text_nonexistent(self):
        from src.image.infrastructure_tesseract_ocr_adapter import TesseractOCRAdapter
        from src.shared.vision_models_vo import FilePath, LanguageCode
        adapter = TesseractOCRAdapter()
        with pytest.raises((RuntimeError, FileNotFoundError)):
            adapter.extract_text(FilePath(value="/nonexistent.png"), LanguageCode(value="eng"))
