"""Vision root MCP entry point dispatching MCP commands to domain containers."""

import logging
import sys
from typing import Any

from mcp.server.fastmcp import FastMCP

from modules.image.src.root_image_container import ImageContainer, build_image_feature
from modules.mcp.src.surface_mcp_action import (
    set_mcp_dispatcher,
    vision_cancel,
    vision_execute,
    vision_help,
    vision_init,
    vision_list_commands,
    vision_status,
)
from modules.shared.src.contract_registry_service_aggregate import (
    RegistryServiceAggregate,
)
from modules.shared.src.taxonomy_vision_vo import CommandName, CommandOutput
from modules.system.src.root_system_container import SystemContainer
from modules.video.src.root_video_container import VideoContainer

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
SYSTEM_COMMANDS = {"init", "get-config", "set-config", "config", "status", "cancel"}


class RootMCPDispatcher(RegistryServiceAggregate):
    """Aggregate dispatcher routing MCP commands to domain orchestrators."""

    # pylint: disable=too-few-public-methods

    def __init__(self) -> None:
        """Initialize domain orchestrators for MCP dispatch."""
        image_feat = build_image_feature()
        self._image = ImageContainer().orchestrator
        self._video = VideoContainer(llm_port=image_feat["llm"]).orchestrator
        self._system = SystemContainer().orchestrator

    def execute_in_process(
        self, command: CommandName, kwargs: dict[str, Any]
    ) -> CommandOutput:
        """Execute a command against the matching domain orchestrator."""
        if command.value in IMAGE_COMMANDS:
            return self._image.execute_in_process(command, kwargs)
        if command.value in VIDEO_COMMANDS:
            return self._video.execute_in_process(command, kwargs)
        if command.value in SYSTEM_COMMANDS:
            return self._system.execute_in_process(command, kwargs)
        raise ValueError(f"Unknown command: {command.value}")


mcp_server = FastMCP("Vision")


def main() -> None:
    """Serve the MCP tools over stdio."""
    logging.basicConfig(level=logging.INFO, stream=sys.stderr)

    logger = logging.getLogger("vision-mcp")
    logger.info("Starting Vision MCP Server (AES architecture)")

    set_mcp_dispatcher(RootMCPDispatcher())

    mcp_server.tool(name="vision_init")(vision_init)
    mcp_server.tool(name="vision_execute")(vision_execute)
    mcp_server.tool(name="vision_list_commands")(vision_list_commands)
    mcp_server.tool(name="vision_help")(vision_help)
    mcp_server.tool(name="vision_status")(vision_status)
    mcp_server.tool(name="vision_cancel")(vision_cancel)

    mcp_server.run(transport="stdio")


if __name__ == "__main__":
    main()
