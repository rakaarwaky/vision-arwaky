"""Unit tests for LLMVisionAdapter._get_session and _encode_image."""

import tempfile
from pathlib import Path

import cv2
import numpy

from modules.image.src.capabilities_llm_vision_adapter import LLMVisionAdapter


class TestLLMVisionAdapter:
    def test_get_session_caches(self, monkeypatch):
        monkeypatch.setenv("LLAMA_API_URL", "http://localhost:1234/v1")
        monkeypatch.setenv("LLAMA_API_KEY", "test-key")
        adapter = LLMVisionAdapter()
        s1 = adapter._get_session()
        s2 = adapter._get_session()
        assert s1 is s2

    def test_encode_image_jpg_mime_type(self):
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            path = f.name
        try:
            img = numpy.zeros((10, 10, 3), dtype=numpy.uint8)
            cv2.imwrite(path, img)
            result = LLMVisionAdapter._encode_image(path)
            assert result.startswith("data:image/jpeg;base64,")
        finally:
            Path(path).unlink(missing_ok=True)

    def test_encode_image_png_mime_type(self):
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            path = f.name
        try:
            img = numpy.zeros((10, 10, 3), dtype=numpy.uint8)
            cv2.imwrite(path, img)
            result = LLMVisionAdapter._encode_image(path)
            assert result.startswith("data:image/png;base64,")
        finally:
            Path(path).unlink(missing_ok=True)

    def test_encode_image_unknown_extension_falls_back_to_png(self):
        with tempfile.NamedTemporaryFile(suffix=".xyz", delete=False) as f:
            path = f.name
        try:
            # Write raw PNG bytes so the file has valid image data
            # but the extension is unknown -> mimetypes.guess_type returns None.
            import cv2 as _cv2
            import numpy as _np

            img = _np.zeros((10, 10, 3), dtype=_np.uint8)
            _, buf = _cv2.imencode(".png", img)
            Path(path).write_bytes(buf.tobytes())
            result = LLMVisionAdapter._encode_image(path)
            assert result.startswith("data:image/png;base64,")
        finally:
            Path(path).unlink(missing_ok=True)
