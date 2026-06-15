from abc import ABC, abstractmethod
from typing import List
from src.taxonomy.vision_models_vo import MemoryEntry, FilePath, MemoryLabel, DistanceThreshold


class VisualMemoryProtocol(ABC):
    """Abstract protocol defining Visual Memory capabilities."""

    @abstractmethod
    def remember_image(self, image_path: FilePath, label: MemoryLabel) -> MemoryEntry:
        """Store image perceptual hash and details in visual memory."""
        pass

    @abstractmethod
    def find_similar_images(self, query_image_path: FilePath, max_distance: DistanceThreshold) -> List[MemoryEntry]:
        """Find visually similar images by computing perceptual hash distance."""
        pass
