"""Visual memory protocol contract."""

from abc import ABC, abstractmethod
from typing import List

from modules.shared.src.common.taxonomy_vision_models_vo import DistanceThreshold, FilePath, MemoryLabel
from modules.shared.src.memory.taxonomy_memory_vo import MemoryEntry


class VisualMemoryProtocol(ABC):
    """Abstract protocol for visual memory store and retrieval."""

    @abstractmethod
    def remember_image(self, image_path: FilePath, label: MemoryLabel) -> MemoryEntry:
        """Store an image in visual memory with a label."""
        ...

    @abstractmethod
    def find_similar_images(
        self, query_image_path: FilePath, max_distance: DistanceThreshold
    ) -> List[MemoryEntry]:
        """Find visually similar images in memory by hamming distance of pHash."""
        ...
