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

    @mcp_server.tool(name="vision_execute")
    def execute(**kwargs):
        """Execute one supported image or video command."""
        return vision_execute(**kwargs)

    @mcp_server.tool(name="vision_list_commands")
    def list_commands(domain: str = ""):
        """Return the supported command catalog, optionally filtered by domain."""
        return vision_list_commands(domain)

    @mcp_server.tool(name="vision_help")
    def help_command(section: str = "all"):
        """Return all or part of the agent-facing project documentation."""
        return vision_help(section)

    @mcp_server.tool(name="vision_status")
    def status():
        """Return runtime dependency and configuration readiness."""
        return vision_status()

    @mcp_server.tool(name="vision_cancel")
    def cancel(job_id: str = ""):
        """Inspect or cancel a tracked job when asynchronous execution is enabled."""
        return vision_cancel(job_id)

    mcp_server.run(transport="stdio")


if __name__ == "__main__":
    main()
