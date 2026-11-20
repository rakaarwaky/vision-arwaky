"""MCP smart-surface command tools — pure delegation to dispatcher and shared utilities."""

import importlib

try:
    _fastmcp_module = importlib.import_module("fastmcp")
except ImportError:
    _fastmcp_module = importlib.import_module("mcp.server.fastmcp")

FastMCP = _fastmcp_module.FastMCP

from modules.shared.src.common.taxonomy_vision_vo import CommandName
from modules.shared.src.contract_registry_service_aggregate import (
    IRegistryServiceAggregate,
)

mcp = FastMCP("Vision")

_dispatcher: IRegistryServiceAggregate | None = None


def set_mcp_dispatcher(dispatcher: IRegistryServiceAggregate | None) -> None:
    """Inject the aggregate facade used by MCP commands."""
    global _dispatcher
    _dispatcher = dispatcher


def get_dispatcher() -> IRegistryServiceAggregate | None:
    """Return the injected aggregate facade if present."""
    return _dispatcher


def _execute_in_process(command: str, kwargs: dict) -> str:
    """Route command to the injected aggregate dispatcher.

    Exceptions propagate to the caller so the MCP framework can report
    them consistently with the CLI surface, which also raises.
    """
    if _dispatcher is None:
        raise RuntimeError(
            "No dispatcher configured. Call set_mcp_dispatcher() before execution."
        )
    cmd_vo = CommandName(value=command)
    return _dispatcher.execute_in_process(cmd_vo, kwargs).value


@mcp.tool()
def vision_init(target_dir: str = ".") -> str:
    """Initialize workspace directory structure and XDG symlinks."""
    return _execute_in_process("init", {"target_dir": target_dir})


@mcp.tool()
def vision_image(image: str, prompt: str = "") -> str:
    """Analyze an image file with AI vision.

    Args:
        image: Path to the image file to analyze
        prompt: Optional analysis prompt to guide the vision model

    Returns:
        JSON-formatted analysis result
    """
    return _execute_in_process("analyze", {"image": image, "prompt": prompt})


@mcp.tool()
def vision_video(video: str, prompt: str = "") -> str:
    """Analyze a video file using frame sampling and VLM.

    Args:
        video: Path to the video file to analyze
        prompt: Optional analysis prompt to guide the video understanding

    Returns:
        JSON-formatted video analysis result
    """
    return _execute_in_process("analyze-video", {"video": video, "prompt": prompt})


@mcp.tool()
def vision_doctor() -> str:
    """Check system dependency readiness and capability status.

    Returns:
        JSON-formatted doctor report showing which system dependencies
        (opencv, numpy, ffmpeg, LLM endpoint, config) are ready and which
        capabilities (image_analysis, video_processing, llm_vision) are available.
    """
    return _execute_in_process("doctor", {})
