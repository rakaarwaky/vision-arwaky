import logging
import sys
from mcp.server.fastmcp import FastMCP
from modules.mcp.src.surface_mcp_action import (
    vision_execute,
    vision_list_commands,
    vision_help,
    vision_status,
    vision_cancel,
)

mcp_server = FastMCP("Vision")


def main():
    logging.basicConfig(level=logging.INFO, stream=sys.stderr)
    logger = logging.getLogger("vision-mcp")
    logger.info("Starting Vision MCP Server (AES architecture)")

    @mcp_server.tool()
    def execute(**kwargs):
        return vision_execute(**kwargs)

    @mcp_server.tool()
    def list_commands(domain: str = ""):
        return vision_list_commands(domain)

    @mcp_server.tool()
    def help(section: str = "all"):
        return vision_help(section)

    @mcp_server.tool()
    def status():
        return vision_status()

    @mcp_server.tool()
    def cancel(job_id: str = ""):
        return vision_cancel(job_id)

    mcp_server.run(transport="stdio")


if __name__ == "__main__":
    main()
