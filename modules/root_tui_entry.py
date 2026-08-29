"""TUI entry point and dispatcher aggregate."""

from modules.cli.src.surface_tui_component import set_tui_dispatcher, tui_main
from modules.image.src.root_image_container import ImageContainer
from modules.shared.src.contract_registry_service_aggregate import (
    RegistryServiceAggregate,
)
from modules.shared.src.taxonomy_vision_vo import CommandName, CommandOutput
from modules.system.src.root_system_container import SystemContainer
from modules.video.src.root_video_container import VideoContainer


class TuiDispatcher(RegistryServiceAggregate):
    """Aggregate dispatcher for TUI operations."""

    def __init__(self) -> None:
        """Initialize dispatcher with orchestrator references."""
        self._image = ImageContainer().orchestrator
        self._video = VideoContainer().orchestrator
        self._system = SystemContainer().orchestrator

    def execute_in_process(
        self, command: CommandName, kwargs: dict[str, object]
    ) -> CommandOutput:
        if command.value in {"analyze", "ocr", "compare"}:
            return self._image.execute_in_process(command, kwargs)
        if command.value in {
            "video-info",
            "extract-frames",
            "check-corruption",
            "detect-scenes",
            "detect-motion",
            "track",
            "analyze-video",
        }:
            return self._video.execute_in_process(command, kwargs)
        if command.value in {"init"}:
            return self._system.execute_in_process(command, kwargs)
        raise ValueError(f"Unknown command: {command.value}")

    def __repr__(self) -> str:
        return "TuiDispatcher()"


def main() -> None:
    """Start the Textual interface with injected dispatcher."""
    set_tui_dispatcher(TuiDispatcher())
    tui_main()


if __name__ == "__main__":
    main()
