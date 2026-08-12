
"""Advanced tests for image processing — orchestrator, LLM adapter, tesseract."""
import json
import os
import tempfile

import cv2
import numpy as np
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


def make_image_processor():
    """Build an ImageProcessingProcessor with real adapters (DI)."""
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

    return ImageProcessingProcessor(
        opencv_port=OpenCVImageAdapter(),
        tesseract_port=TesseractOCRAdapter(),
        llm_port=LLMVisionAdapter(),
    )


def make_image_orchestrator():
    """Build an ImageOrchestrator with injected ports (DI)."""
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
    return ImageOrchestrator(
        image_processing=processor,
        opencv=opencv,
        tesseract=tesseract,
        llm=llm,
    )


class TestImageOrchestrator:
    def test_get_image_processing(self):
        proc = make_image_processor()
        assert proc is not None
        img = create_test_image()
        path = save_test_image(img)
        try:
            from modules.shared.src.taxonomy_vision_models_vo import FilePath
            elements = proc.find_elements(FilePath(value=path))
            assert isinstance(elements, list)
        finally:
            os.unlink(path)

    def test_execute_image_cmd_analyze_no_llm(self):
        from modules.shared.src.taxonomy_vision_models_vo import CommandName

        orch = make_image_orchestrator()
        img = create_test_image()
        path = save_test_image(img)
        try:
            result = orch.execute_in_process(
                CommandName(value="analyze"), {"image": path}
            )
            assert result is not None
            data = json.loads(result.value)
            assert "source" in data
        finally:
            os.unlink(path)

    def test_execute_image_cmd_ocr(self):
        from modules.shared.src.taxonomy_vision_models_vo import CommandName

        orch = make_image_orchestrator()
        img = create_test_image()
        path = save_test_image(img)
        try:
            result = orch.execute_in_process(
                CommandName(value="ocr"), {"image": path, "lang": "eng"}
            )
            assert result is not None
        finally:
            os.unlink(path)

    def test_execute_image_cmd_elements(self):
        from modules.shared.src.taxonomy_vision_models_vo import CommandName

        orch = make_image_orchestrator()
        img = create_test_image()
        path = save_test_image(img)
        try:
            result = orch.execute_in_process(
                CommandName(value="elements"), {"image": path}
            )
            assert result is not None
            data = json.loads(result.value)
            assert isinstance(data, list)
        finally:
            os.unlink(path)

    def test_execute_image_cmd_compare(self):
        from modules.shared.src.taxonomy_vision_models_vo import CommandName

        orch = make_image_orchestrator()
        img = create_test_image()
        p1 = save_test_image(img)
        p2 = save_test_image(img)
        try:
            result = orch.execute_in_process(
                CommandName(value="compare"), {"image1": p1, "image2": p2}
            )
            assert result is not None
            data = json.loads(result.value)
            assert "identical" in data
        finally:
            os.unlink(p1)
            os.unlink(p2)

    def test_execute_image_cmd_unknown(self):
        from modules.shared.src.taxonomy_vision_models_vo import CommandName

        orch = make_image_orchestrator()
        with pytest.raises(ValueError):
            orch.execute_in_process(CommandName(value="nonexistent"), {})

    def test_orchestrator_ports(self):
        orch = make_image_orchestrator()
        assert orch._opencv is not None
        assert orch._tesseract is not None
        assert orch._llm is not None
        assert orch._image_processing is not None


class TestLLMVisionAdapter:
    def test_adapter_properties(self):
        from modules.image.src.capabilities_llm_vision_adapter import LLMVisionAdapter
        adapter = LLMVisionAdapter()
        assert adapter.config is not None
        assert isinstance(adapter.backend, str)
        assert adapter.model is not None

    def test_adapter_find_free_port(self):
        from modules.image.src.capabilities_llm_vision_adapter import LLMVisionAdapter
        port = LLMVisionAdapter._find_free_port()
        assert isinstance(port, int)
        assert port > 0
        assert port < 65536

    def test_adapter_bundled_path(self):
        from modules.image.src.capabilities_llm_vision_adapter import LLMVisionAdapter
        path = LLMVisionAdapter._get_bundled_server_path(LLMVisionAdapter)
        assert path is None or path.exists()


class TestTesseractAdapter:
    def test_extract_text_nonexistent(self):
        from modules.image.src.capabilities_tesseract_ocr_adapter import (
            TesseractOCRAdapter,
        )
        from modules.shared.src.taxonomy_vision_models_vo import FilePath, LanguageCode
        adapter = TesseractOCRAdapter()
        with pytest.raises((RuntimeError, FileNotFoundError)):
            adapter.extract_text(FilePath(value="/nonexistent.png"), LanguageCode(value="eng"))
