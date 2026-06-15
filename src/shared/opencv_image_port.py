from abc import ABC, abstractmethod


class OpenCVImagePort(ABC):
    """Abstract port defining OpenCV image and video operations."""

    @property
    @abstractmethod
    def cv2(self):
        """Expose raw cv2 namespace for standard operations."""
        pass

    @property
    @abstractmethod
    def np(self):
        """Expose numpy namespace."""
        pass

    @abstractmethod
    def read_image(self, path):
        """Read image from path."""
        pass

    @abstractmethod
    def write_image(self, path, image):
        """Write image to path."""
        pass

    @abstractmethod
    def get_video_capture(self, path):
        """Get VideoCapture object."""
        pass

    @abstractmethod
    def get_dimensions(self, image):
        """Get image width and height."""
        pass

    @abstractmethod
    def to_grayscale(self, image):
        """Convert BGR image to grayscale."""
        pass

    @abstractmethod
    def detect_edges(self, image, t1 = 50, t2 = 150):
        """Perform Canny edge detection."""
        pass

    @abstractmethod
    def find_contours(self, edges):
        """Find contours from edge map."""
        pass

    @abstractmethod
    def get_contour_area(self, contour):
        """Get contour area."""
        pass

    @abstractmethod
    def get_bounding_box(self, contour):
        """Get x, y, width, height bounding box for a contour."""
        pass

    @abstractmethod
    def abs_diff(self, img1, img2):
        """Compute absolute difference between two images."""
        pass

    @abstractmethod
    def calc_optical_flow(self, prev, next_img):
        """Calculate optical flow between consecutive frames."""
        pass

    @abstractmethod
    def compare_histograms(self, h1, h2):
        """Compare two color histograms."""
        pass

    @abstractmethod
    def compute_phash(self, image):
        """Compute perceptual hash of an image."""
        pass
