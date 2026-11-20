"""MCP smart-surface command tools — pure delegation to dispatcher and shared utilities."""

import importlib
import json

try:
    _fastmcp_module = importlib.import_module("fastmcp")
except ImportError:
    _fastmcp_module = importlib.import_module("mcp.server.fastmcp")

FastMCP = _fastmcp_module.FastMCP

from modules.shared.src.contract_registry_service_aggregate import (
    IRegistryServiceAggregate,
)
from modules.shared.src.taxonomy_vision_constant import DEFAULT_MODELS_TIMEOUT_S
from modules.shared.src.taxonomy_vision_vo import CommandName
from modules.shared.src.utility_config_handler import (
    find_active_config,
    load_merged_config,
    resolve_external_settings,
)
from modules.shared.src.utility_dependency_checker import check_all_dependencies
from modules.shared.src.utility_llm_check import check_llm_endpoint
from modules.shared.src.utility_version_resolver import get_package_version

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
def vision_execute(
    command: str,
    video: str = "",
    image: str = "",
    prompt: str = "",
    target_dir: str = ".",
) -> str:
    """Execute safe vision commands."""
    kwargs = {
        "image": image,
        "video": video,
        "prompt": prompt,
        "target_dir": target_dir,
    }
    return _execute_in_process(command, kwargs)


@mcp.tool()
def vision_list_commands(domain: str = "") -> str:
    """List all available vision commands."""
    commands = {
        "workspace": [
            {
                "command": "init",
                "args": "[target_dir]",
                "desc": "Initialize workspace with .vision-arwaky symlinks",
            }
        ],
        "image": [
            {
                "command": "analyze",
                "args": "image, [prompt]",
                "desc": "Analyze image with AI vision",
            },
        ],
        "video": [
            {
                "command": "analyze-video",
                "args": "video, [prompt]",
                "desc": "Analyze sampled video frames with a VLM and summarize the video",
            },
        ],
    }

    if domain and domain in commands:
        return json.dumps(commands[domain], indent=2)
    return json.dumps(commands, indent=2)


@mcp.tool()
def vision_help(section: str = "all") -> str:
    """Return workspace documentation for vision commands."""
    content = """Vision Arwaky: workspace init, image analysis, and video analysis.

## workspace
  init [target_dir]       Initialize workspace with .vision-arwaky symlinks

## image
  image <path>            Analyze an image with AI vision

## video
  video <path>            Analyze sampled video frames with a VLM and summarize

Troubleshooting: use the `vision_status` MCP tool to check dependencies and LLM endpoint connectivity."""

    if section == "all":
        return content

    requested = section.strip().lower()
    sections = content.split("\n## ")
    for s in sections[1:]:
        heading = s.splitlines()[0].strip().lower()
        if (
            heading == requested
            or heading.endswith(f": {requested}")
            or heading.startswith(f"{requested}:")
        ):
            return "## " + s

    return f"Section '{section}' not found. Available: all, image, video, workspace"


@mcp.tool()
def vision_status() -> str:
    """Check vision server status, dependencies, and capabilities."""
    config = load_merged_config()
    base_url, api_key, model = resolve_external_settings(config)
    selected_backend = str(config.get("backend", "external"))

    deps = check_all_dependencies()
    llm_ready, llm_status = check_llm_endpoint(
        base_url, api_key, timeout=DEFAULT_MODELS_TIMEOUT_S
    )
    deps["llm_endpoint"] = llm_status

    config_path = find_active_config()
    pkg_version = get_package_version()
    status: dict = {
        "server": f"vision-mcp v{pkg_version}",
        "pattern": "hybrid (6 MCP tools + unlimited CLI)",
        "configuration": {
            "config_yaml_detected": config_path is not None,
            "config_source": str(config_path) if config_path else "none",
            "selected_backend": selected_backend,
            "llm_endpoint": base_url,
            "llm_model": model or None,
            "llm_api_key_configured": bool(api_key),
        },
        "dependencies": deps,
        "capabilities": {
            "image_analysis": deps.get("opencv") == "OK",
            "video_processing": deps.get("opencv") == "OK"
            and deps.get("ffmpeg") == "OK",
            "llm_vision": llm_ready,
        },
    }
    return json.dumps(status, indent=2)


@mcp.tool()
def vision_cancel(job_id: str = "") -> str:
    """Cancel a running vision operation via system dispatcher."""
    return _execute_in_process("cancel", {"job_id": job_id})
