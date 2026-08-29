"""OpenCV utility functions — stateless, pure, domain-agnostic computer vision operations.

Module-level functions only — no classes, no state.
"""

from __future__ import annotations

import logging
from typing import Any

import cv2
import numpy

from modules.shared.src.taxonomy_vision_models_vo import (
    BoundingBox,
    FilePath,
    VideoInfo,
)

logger = logging.getLogger("mcp_server.utility.opencv")


def read_image(path: str | FilePath) -> numpy.ndarray | None:
    """Read an image from disk.

    Args:
        path: Path to the image file.

    Returns:
        Image as a NumPy array (BGR format) or None if reading failed.
    """
    p = path.value if isinstance(path, FilePath) else str(path)
    return cv2.imread(p)


def write_image(path: str | FilePath, image: numpy.ndarray) -> bool:
    """Write an image to disk.

    Args:
        path: Target file path.
        image: Image NumPy array.

    Returns:
        True if the image was successfully saved, False otherwise.
    """
    p = path.value if isinstance(path, FilePath) else str(path)
    return bool(cv2.imwrite(p, image))


def to_grayscale(image: numpy.ndarray) -> numpy.ndarray:
    """Convert an image or frame to grayscale.

    Args:
        image: Source BGR image array.

    Returns:
        Grayscale single-channel image array.
    """
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def compute_abs_diff(img1: numpy.ndarray, img2: numpy.ndarray) -> numpy.ndarray:
    """Compute per-element absolute difference between two image arrays.

    Args:
        img1: First image array.
        img2: Second image array.

    Returns:
        Absolute difference array.
    """
    return cv2.absdiff(img1, img2)


def detect_edges(
    image: numpy.ndarray, t1: int = 50, t2: int = 150
) -> numpy.ndarray:
    """Detect edges in an image using the Canny algorithm.

    Args:
        image: Grayscale or BGR image.
        t1: First threshold for the hysteresis procedure.
        t2: Second threshold for the hysteresis procedure.

    Returns:
        Binary edge map array.
    """
    return cv2.Canny(image, t1, t2)


def find_contours(edges_or_mask: numpy.ndarray) -> list[numpy.ndarray]:
    """Find external contours in a binary edge map or mask.

    Args:
        edges_or_mask: 8-bit single-channel binary image.

    Returns:
        List of detected contours.
    """
    contours, _ = cv2.findContours(
        edges_or_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    return list(contours)


def get_contour_area(contour: Any) -> float:
    """Compute the area of a contour.

    Args:
        contour: Input 2D point vector.

    Returns:
        Calculated contour area.
    """
    return float(cv2.contourArea(contour))


def get_bounding_box(contour: Any) -> BoundingBox:
    """Compute the minimal bounding box for a 2D contour.

    Args:
        contour: Input 2D point vector.

    Returns:
        BoundingBox value object with (x, y, width, height).
    """
    x, y, w, h = cv2.boundingRect(contour)
    return BoundingBox(x=int(x), y=int(y), width=int(w), height=int(h))


def compare_histograms(h1: numpy.ndarray, h2: numpy.ndarray) -> float:
    """Compare two color histograms using correlation.

    Args:
        h1: First histogram array.
        h2: Second histogram array.

    Returns:
        Correlation metric (between -1.0 and 1.0).
    """
    return float(cv2.compareHist(h1, h2, cv2.HISTCMP_CORREL))


def compute_phash(image: numpy.ndarray) -> str:
    """Compute a perceptual hash (pHash) for an image.

    Args:
        image: Source image array.

    Returns:
        Hex-encoded hash string.
    """
    try:
        img_hash = getattr(cv2, "img_hash", None)
        if img_hash is None:
            resized = cv2.resize(image, (8, 8), interpolation=cv2.INTER_AREA)
            gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
            avg = gray.mean()
            hash_bits = (gray > avg).flatten()
            return "".join(["1" if b else "0" for b in hash_bits])

        hasher_creator = getattr(img_hash, "PHash_create", None)
        if hasher_creator is None:
            raise AttributeError("PHash_create not found in img_hash")

        hasher = hasher_creator()
        hash_val = hasher.compute(image)
        return hash_val.tobytes().hex()
    except (AttributeError, RuntimeError, TypeError, ValueError, cv2.error) as e:
        logger.warning(f"pHash computation fallback used: {e}")
        return str(hash(image.tobytes()))


def open_video_capture(path: str | FilePath) -> cv2.VideoCapture:
    """Open a video capture stream for a file.

    Args:
        path: Path to the video file.

    Returns:
        VideoCapture instance.
    """
    p = path.value if isinstance(path, FilePath) else str(path)
    return cv2.VideoCapture(p)


def get_video_metadata(video_path: FilePath) -> VideoInfo:
    """Read structural metadata from a video file.

    Args:
        video_path: Path to the video file.

    Returns:
        VideoInfo value object.
    """
    cap = open_video_capture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Failed to open video file: {video_path.value}")

    fps = float(cap.get(cv2.CAP_PROP_FPS))
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()

    return VideoInfo(
        fps=fps,
        frame_count=frame_count,
        width=width,
        height=height,
    )


def check_video_corruption(video_path: FilePath) -> bool:
    """Check if a video file can be opened and decoded properly.

    Args:
        video_path: Path to the video file.

    Returns:
        True if corrupted or unreadable, False if healthy.
    """
    cap = open_video_capture(video_path)
    is_open = cap.isOpened()
    if is_open:
        success, _ = cap.read()
        is_open = success
    cap.release()
    return not is_open


def calc_optical_flow(
    prev: numpy.ndarray, next_img: numpy.ndarray
) -> numpy.ndarray:
    """Calculate dense optical flow using the Farneback algorithm.

    Args:
        prev: First 8-bit single-channel input image.
        next_img: Second input image of the same size and the same type as prev.

    Returns:
        Computed optical flow map array (2-channel float32).
    """
    flow: Any = None
    return cv2.calcOpticalFlowFarneback(
        prev, next_img, flow, 0.5, 3, 15, 3, 5, 1.2, 0
    )
