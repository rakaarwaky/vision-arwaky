"""OpenCV Feature Composition Root Container.

Wires OpenCV infrastructure adapter.
"""

from modules.opencv.src.capabilities_opencv_image_adapter import OpenCVImageAdapter


def build_opencv() -> OpenCVImageAdapter:
    """Instantiate OpenCV image adapter."""
    return OpenCVImageAdapter()
