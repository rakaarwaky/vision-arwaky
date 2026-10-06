"""TUI entry point and dispatcher aggregate."""

from modules.cli.src.surface_tui_controller import set_tui_dispatcher, tui_main
from modules.image.src.root_image_container import ImageContainer, build_image_feature
from modules.shared.src.contract_registry_service_aggregate import (
    IRegistryServiceAggregate,
)
from modules.shared.src.taxonomy_command_vo import CommandDomain
from modules.shared.src.taxonomy_vision_vo import (
    CommandName,
    CommandOutput,
    SystemCommandParams,
)
from modules.system.src.root_system_container import SystemContainer
from modules.video.src.root_video_container import VideoContainer


class TuiDispatcher(IRegistryServiceAggregate):
    """Aggregate dispatcher for TUI operations."""

    def __init__(self) -> None:
        """Initialize dispatcher with orchestrator references."""
        image_feat = build_image_feature()
        self._image = ImageContainer(llm_port=image_feat["llm"]).orchestrator
        self._video = VideoContainer(llm_port=image_feat["llm"]).orchestrator
        self._system = SystemContainer().orchestrator

    def execute_in_process(
        self,
        command: CommandName,
        kwargs: dict | SystemCommandParams,
    ) -> CommandOutput:
        domain = CommandDomain.from_command(command.value)
        if domain == CommandDomain.IMAGE:
            return self._image.execute_in_process(command, kwargs)
        if domain == CommandDomain.VIDEO:
            return self._video.execute_in_process(command, kwargs)
        return self._system.execute_in_process(command, kwargs)

    def __repr__(self) -> str:
        return "TuiDispatcher()"


def main() -> None:
    """Start the Textual interface with injected dispatcher."""
    set_tui_dispatcher(TuiDispatcher())
    tui_main()


if __name__ == "__main__":
    main()
