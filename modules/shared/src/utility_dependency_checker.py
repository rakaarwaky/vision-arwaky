"""Dependency checking utility — stateless single source of truth."""

from __future__ import annotations

import shutil

PYTHON_DEPS: dict[str, str] = {
    "opencv": "cv2",
    "pillow": "PIL",
    "numpy": "numpy",
    "pytesseract": "pytesseract",
    "requests": "requests",
    "pyyaml": "yaml",
}

BINARY_DEPS: list[str] = ["ffmpeg", "ffprobe", "tesseract"]


def check_python_dependencies() -> dict[str, str]:
    """Check availability of python dependencies."""
    result: dict[str, str] = {}
    for name, module in PYTHON_DEPS.items():
        try:
            __import__(module)
            result[name] = "OK"
        except ImportError:
            result[name] = "MISSING"
    return result


def check_binary_dependencies() -> dict[str, str]:
    """Check availability of CLI binary dependencies."""
    return {name: "OK" if shutil.which(name) else "MISSING" for name in BINARY_DEPS}


def check_all_dependencies() -> dict[str, str]:
    """Check both python and binary dependencies."""
    deps = check_python_dependencies()
    deps.update(check_binary_dependencies())
    return deps
