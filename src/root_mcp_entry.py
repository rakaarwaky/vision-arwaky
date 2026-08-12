"""MCP Server Entry Point — thin entry that wires deps → action surface.

Mirrors lint-arwaky's root_mcp_main_entry.rs pattern:
1. Initialize logging
2. Build common dependencies (root_container)
3. Wrap deps into action surface (McpActionSurface)
4. Register MCP tools that delegate to the surface
5. Serve on stdio transport

This replaces the old monolithic tool handler with a clean delegation pattern.
"""

import logging
import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP

# Import the action surface (business logic delegation layer)
from src.surface_mcp_action import McpActionSurface

# Project root (3 levels up from this file)
VISION_PROJECT = str(Path(__file__).resolve().parents[2])


def main():
    """Entry point for the Vision MCP server."""
    logging.basicConfig(level=logging.INFO, stream=sys.stderr)
    logger = logging.getLogger("vision-mcp")
    logger.info("Starting Vision MCP Server (AES architecture)")

    # ─── Build deps & wire action surface ─────────────────────────────
    mcp_server = FastMCP("Vision")
    action_surface = McpActionSurface()

    # ─── Register MCP tools (delegate to action surface) ──────────────

    @mcp_server.tool()
    def vision_execute(
        command: str,
        image: str = "",
        image1: str = "",
        image2: str = "",
        video: str = "",
        input_path: str = "",
        output_path: str = "",
        lang: str = "eng",
        prompt: str = "",
        threshold: float = 30.0,
        min_area: int = 500,
        bbox: str = "",
        max_frames: int = 300,
        interval: float = 1.0,
        start: float = 0.0,
        duration: float = 0.0,
        label: str = "",
        query: str = "",
        max_distance: int = 15,
    ) -> str:
        """Execute ANY vision command via action surface delegate."""
        kwargs = {
            "image": image,
            "image1": image1,
            "image2": image2,
            "video": video,
            "input_path": input_path,
            "output_path": output_path,
            "lang": lang,
            "prompt": prompt,
            "threshold": threshold,
            "min_area": min_area,
            "bbox": bbox,
            "max_frames": max_frames,
            "interval": interval,
            "start": start,
            "duration": duration,
            "label": label,
            "query": query,
            "max_distance": max_distance,
        }
        return action_surface.execute_command(command, kwargs)

    @mcp_server.tool()
    def vision_list_commands(domain: str = "") -> str:
        """List all available vision commands via action surface delegate."""
        return action_surface.list_commands(domain)

    @mcp_server.tool()
    def vision_help(section: str = "all") -> str:
        """Read SKILL.md documentation via action surface delegate."""
        return action_surface.get_help(section)

    @mcp_server.tool()
    def vision_status() -> str:
        """Check server status, dependencies, capabilities via action surface."""
        return action_surface.health_check()

    @mcp_server.tool()
    def vision_cancel(job_id: str = "") -> str:
        """Cancel a running operation via action surface delegate."""
        return action_surface.cancel(job_id)

    # ─── Start server ────────────────────────────────────────────────
    mcp_server.run(transport="stdio")


if __name__ == "__main__":
    main()
