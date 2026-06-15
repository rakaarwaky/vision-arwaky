import cv2 as _cv2
import numpy as _np
from typing import Optional, Tuple
import logging
from src.contract import OpenCVImagePort
from src.taxonomy import BoundingBox, FilePath

logger = logging.getLogger("mcp_server.infrastructure.opencv")


class OpenCVImageAdapter(OpenCVImagePort):
    """Infrastructure adapter for OpenCV operations."""

    _taxonomy_marker = BoundingBox

    @property
    def cv2(self):
        return _cv2

    @property
    def np(self):
        return _np

    def read_image(self, path: str | FilePath) -> Optional[_np.ndarray]:
        p = path.value if isinstance(path, FilePath) else str(path)
        return _cv2.imread(p)

    def write_image(self, path: str | FilePath, image: _np.ndarray) -> bool:
        p = path.value if isinstance(path, FilePath) else str(path)
        return bool(_cv2.imwrite(p, image))

    def get_video_capture(self, path: str | FilePath) -> _cv2.VideoCapture:
        p = path.value if isinstance(path, FilePath) else str(path)
        return _cv2.VideoCapture(p)

    def get_dimensions(self, image: _np.ndarray) -> Tuple[int, int]:
        h, w = image.shape[:2]
        return w, h

    def to_grayscale(self, image: _np.ndarray) -> _np.ndarray:
        return _cv2.cvtColor(image, _cv2.COLOR_BGR2GRAY)

    def detect_edges(self, image: _np.ndarray, t1: int = 50, t2: int = 150) -> _np.ndarray:
        return _cv2.Canny(image, t1, t2)

    def find_contours(self, edges: _np.ndarray) -> list:
        contours, _ = _cv2.findContours(
            edges, _cv2.RETR_EXTERNAL, _cv2.CHAIN_APPROX_SIMPLE
        )
        return list(contours)

    def get_contour_area(self, contour) -> float:
        return float(_cv2.contourArea(contour))

    def get_bounding_box(self, contour) -> Tuple[int, int, int, int]:
        x, y, w, h = _cv2.boundingRect(contour)
        return int(x), int(y), int(w), int(h)

    def abs_diff(self, img1: _np.ndarray, img2: _np.ndarray) -> _np.ndarray:
        return _cv2.absdiff(img1, img2)

    def calc_optical_flow(self, prev: _np.ndarray, next_img: _np.ndarray) -> _np.ndarray:
        flow: Optional[_np.ndarray] = None
        result = _cv2.calcOpticalFlowFarneback(
            prev, next_img, flow, 0.5, 3, 15, 3, 5, 1.2, 0
        )
        return result

    def compare_histograms(self, h1: _np.ndarray, h2: _np.ndarray) -> float:
        return float(_cv2.compareHist(h1, h2, _cv2.HISTCMP_CORREL))

    def compute_phash(self, image: _np.ndarray) -> str:
        # Requires opencv-contrib-python for img_hash, falling back to simple hash if missing
        try:
            img_hash = getattr(_cv2, "img_hash", None)
            if img_hash is None:
                # Simple average hash as fallback
                resized = _cv2.resize(image, (8, 8), interpolation=_cv2.INTER_AREA)
                gray = _cv2.cvtColor(resized, _cv2.COLOR_BGR2GRAY)
                avg = gray.mean()
                hash_bits = (gray > avg).flatten()
                return "".join(["1" if b else "0" for b in hash_bits])

            hasher_creator = getattr(img_hash, "PHash_create", None)
            if hasher_creator is None:
                raise AttributeError("PHash_create not found in img_hash")

            hasher = hasher_creator()
            hash_val = hasher.compute(image)
            return hash_val.tobytes().hex()
        except Exception as e:
            logger.warning(f"pHash computation failed, using basic hash: {e}")
            return str(hash(image.tobytes()))
