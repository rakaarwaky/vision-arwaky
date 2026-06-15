"""Memory Agent Orchestrator — coordinates visual memory capabilities."""

import importlib
import json
import os
from typing import Any, Dict

from src.shared.vision_models_vo import FilePath, MemoryLabel, DistanceThreshold


class MemoryOrchestrator:
    """Orchestrator for visual memory domain."""

    @staticmethod
    def get_opencv():
        module = importlib.import_module("src.opencv.infrastructure_opencv_image_adapter")
        cls = getattr(module, "OpenCVImageAdapter")
        return cls()

    @staticmethod
    def get_utils():
        module = importlib.import_module("src.system_utils.infrastructure_system_utils_util")
        cls = getattr(module, "SystemUtilsUtil")
        return cls()

    @staticmethod
    def get_visual_memory():
        cap_mod = importlib.import_module("src.memory.capabilities_visual_memory_store")
        cap_cls = getattr(cap_mod, "VisualMemoryStore")
        return cap_cls(
            opencv_port=MemoryOrchestrator.get_opencv(),
            utils_port=MemoryOrchestrator.get_utils(),
        )

    @staticmethod
    def execute_memory_cmd(command: str, kwargs: Dict[str, Any]) -> str | None:
        """Execute memory-related commands."""
        cap = MemoryOrchestrator.get_visual_memory()

        if command == "memory-store":
            img = FilePath(value=kwargs["image"])
            label = MemoryLabel(value=kwargs["label"])
            return json.dumps(cap.remember_image(img, label).model_dump(), indent=2)
        elif command == "memory-search":
            query = FilePath(value=kwargs["query"])
            max_dist_val = int(kwargs["max_distance"])
            max_distance = DistanceThreshold(value=max_dist_val)
            res = cap.find_similar_images(query, max_distance)
            return json.dumps([r.model_dump() for r in res], indent=2)
        elif command == "memory-list":
            memory_dir = os.path.expanduser("~/.vision-memory")
            index_file = os.path.join(memory_dir, "index.json")
            if os.path.exists(index_file):
                with open(index_file) as f:
                    data = json.load(f)
                return json.dumps(data, indent=2)
            return json.dumps({})
        return None
