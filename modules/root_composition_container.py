"""Root Composition Container — Composition root for dependency injection.

Wires all feature modules together by composing per-feature containers.
"""

from typing import Any

from modules.image.src.root_image_container import build_image_feature
from modules.shared.src.contract_registry_service_aggregate import (
    RegistryServiceAggregate,
)
from modules.shared.src.taxonomy_vision_models_vo import CommandName, CommandOutput
from modules.video.src.root_video_container import build_video_feature

IMAGE_COMMANDS = {"analyze", "ocr", "compare"}
VIDEO_COMMANDS = {
    "video-info",
    "extract-frames",
    "check-corruption",
    "detect-scenes",
    "detect-motion",
    "track",
    "analyze-video",
}


class RootDispatcher(RegistryServiceAggregate):
    """Composition-root facade routing commands to per-domain orchestrators."""

    def __init__(self, graph: dict[str, Any]):
        self._graph = graph

    def execute_in_process(
        self, command: CommandName, kwargs: dict[str, Any]
    ) -> CommandOutput:
        if command.value in IMAGE_COMMANDS:
            return self._graph["image_orchestrator"].execute_in_process(command, kwargs)
        if command.value in VIDEO_COMMANDS:
            return self._graph["video_orchestrator"].execute_in_process(command, kwargs)
        raise ValueError(f"Unknown command: {command.value}")


def build() -> dict[str, Any]:
    """Compose all feature containers into unified application graph."""
    image_feature = build_image_feature()
    video_feature = build_video_feature(llm_port=image_feature["llm"])

    graph = {
        "tesseract": image_feature["tesseract"],
        "llm": image_feature["llm"],
        "image_processing": image_feature["image_processing"],
        "image_orchestrator": image_feature["image_orchestrator"],
        "ffmpeg": video_feature["ffmpeg"],
        "video_processing": video_feature["video_processing"],
        "video_analysis": video_feature["video_analysis"],
        "object_tracking": video_feature["object_tracking"],
        "video_orchestrator": video_feature["video_orchestrator"],
    }
    graph["dispatcher"] = RootDispatcher(graph)
    return graph


