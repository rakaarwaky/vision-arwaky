from abc import ABC, abstractmethod
from typing import Any

from modules.shared.src.taxonomy_vision_models_vo import FilePath


class OpenCVImageProtocol(ABC):
    """Abstract port defining OpenCV image and video operations."""

    @property
    @abstractmethod
    def cv2(self):
        """Expose raw cv2 namespace for standard operations."""

    @property
    @abstractmethod
    def np(self):
        """Expose numpy namespace."""

    @abstractmethod
    def read_image(self, path: FilePath | str):
        """Read image from path."""

    @abstractmethod
    def write_image(self, path: FilePath | str, image) -> bool:
        """Write image to path."""

    @abstractmethod
    def get_video_capture(self, path: FilePath | str):
        """Get VideoCapture object."""

    @abstractmethod
    def get_dimensions(self, image) -> tuple[int, int]:
        """Get image width and height."""

    @abstractmethod
    def to_grayscale(self, image):
        """Convert BGR image to grayscale."""

    @abstractmethod
    def detect_edges(self, image, t1: int = 50, t2: int = 150):
        """Perform Canny edge detection."""

    @abstractmethod
    def find_contours(self, edges) -> list[Any]:
        """Find contours from edge map."""

    @abstractmethod
    def get_contour_area(self, contour) -> Any:
        """Get contour area."""

    @abstractmethod
    def get_bounding_box(self, contour) -> tuple[int, int, int, int]:
        """Get x, y, width, height bounding box for a contour."""

    @abstractmethod
    def abs_diff(self, img1, img2):
        """Compute absolute difference between two images."""

    @abstractmethod
    def calc_optical_flow(self, prev, next_img):
        """Calculate optical flow between consecutive frames."""

    @abstractmethod
    def compare_histograms(self, h1, h2) -> Any:
        """Compare two color histograms."""

    @abstractmethod
    def compute_phash(self, image) -> Any:
        """Compute perceptual hash of an image."""
