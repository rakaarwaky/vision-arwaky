import logging
import sys

from mcp.server.fastmcp import FastMCP

from modules.mcp.src.surface_mcp_action import (
    set_mcp_dispatcher,
    vision_cancel,
    vision_execute,
    vision_help,
    vision_list_commands,
    vision_status,
)
from modules.root_composition_container import build

mcp_server = FastMCP("Vision")


def main() -> None:
    """Build the dependency graph and serve the MCP tools over stdio."""
    graph = build()
    set_mcp_dispatcher(graph["dispatcher"])

    logging.basicConfig(level=logging.INFO, stream=sys.stderr)
    logger = logging.getLogger("vision-mcp")
    logger.info("Starting Vision MCP Server (AES architecture)")

    mcp_server.tool(name="vision_execute")(vision_execute)
    mcp_server.tool(name="vision_list_commands")(vision_list_commands)
    mcp_server.tool(name="vision_help")(vision_help)
    mcp_server.tool(name="vision_status")(vision_status)

    # Serve the MCP protocol over stdio. Without this the daemon exits
    # immediately after registering tools and clients see "connection closed".
    mcp_server.run(transport="stdio")
if __name__ == "__main__":
    main()
