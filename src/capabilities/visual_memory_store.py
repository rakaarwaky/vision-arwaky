"""Visual memory: store and retrieve images by perceptual hash."""

import os
import json
from pathlib import Path
from typing import List
from src.contract import VisualMemoryProtocol
from src.contract import OpenCVImagePort
from src.contract import SystemUtilsPort
from src.taxonomy.vision_models_vo import MemoryEntry, FilePath, MemoryLabel, DistanceThreshold


class VisualMemoryStore(VisualMemoryProtocol):
    """Store images in memory and find similar ones by perceptual hashing."""

    MEMORY_DIR = os.path.expanduser("~/.vision-memory")
    INDEX_FILE = os.path.join(MEMORY_DIR, "index.json")

    def __init__(self, opencv_port: OpenCVImagePort, utils_port: SystemUtilsPort):
        self._opencv = opencv_port
        self._utils = utils_port
        os.makedirs(self.MEMORY_DIR, exist_ok=True)
        self._index = self._load_index()

    def _load_index(self) -> dict:
        if os.path.exists(self.INDEX_FILE):
            try:
                with open(self.INDEX_FILE) as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}

    def _save_index(self):
        with open(self.INDEX_FILE, "w") as f:
            json.dump(self._index, f, indent=2)

    def _compute_phash(self, image_path: str) -> str:
        """Compute perceptual hash of an image."""
        img = self._opencv.read_image(image_path)
        if img is None:
            raise ValueError(f"Cannot read image: {image_path}")
        return self._opencv.compute_phash(img)

    def remember_image(self, image_path: FilePath, label: MemoryLabel) -> MemoryEntry:
        """Store an image in visual memory with a label."""
        abs_path = str(Path(image_path.value).resolve())
        if not os.path.exists(abs_path):
            raise FileNotFoundError(f"Image not found: {abs_path}")

        phash = self._compute_phash(abs_path)
        label_val = label.value if label else "unknown"
        entry = MemoryEntry(
            label=label_val,
            phash=phash,
            image_path=abs_path,
            metadata={"stored_at": str(os.path.getctime(abs_path))},
        )

        # Store in index (keyed by phash)
        self._index[phash] = entry.model_dump()
        self._index[phash]["label"] = label_val  # force raw string in index JSON
        self._save_index()

        return entry

    def find_similar_images(self, query_image_path: FilePath, max_distance: DistanceThreshold) -> List[MemoryEntry]:
        """Find visually similar images in memory by hamming distance of pHash."""
        abs_path = str(Path(query_image_path.value).resolve())
        if not os.path.exists(abs_path):
            raise FileNotFoundError(f"Image not found: {abs_path}")

        query_hash = self._compute_phash(abs_path)
        results = []
        max_dist_val = max_distance.value if max_distance else 15

        for stored_hash, entry_data in self._index.items():
            dist = self._hamming_distance(query_hash, stored_hash)
            if dist <= max_dist_val:
                metadata = entry_data.get("metadata", {})
                metadata["distance"] = dist
                results.append(
                    MemoryEntry(
                        label=entry_data["label"],
                        phash=entry_data["phash"],
                        image_path=entry_data["image_path"],
                        metadata=metadata,
                    )
                )

        # Sort by distance (most similar first)
        results.sort(key=lambda x: x.metadata.get("distance", 0))
        return results

    @staticmethod
    def _hamming_distance(hash1: str, hash2: str) -> int:
        """Compute hamming distance between two binary hash strings."""
        if len(hash1) != len(hash2):
            # Handle different hash formats
            min_len = min(len(hash1), len(hash2))
            hash1 = hash1[:min_len]
            hash2 = hash2[:min_len]
        return sum(c1 != c2 for c1, c2 in zip(hash1, hash2))
