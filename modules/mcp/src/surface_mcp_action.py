"""MCP surface — pure delegation to dispatcher and shared utilities."""

import json
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

from modules.shared.src.contract_registry_service_aggregate import (
    RegistryServiceAggregate,
)
from modules.shared.src.taxonomy_vision_constant import (
    DEFAULT_MODELS_TIMEOUT_S,
    EMBEDDED_SKILL_MD,
)
from modules.shared.src.taxonomy_vision_vo import CommandName
from modules.shared.src.utility_config_handler import (
    find_active_config,
    load_merged_config,
    resolve_external_settings,
)
from modules.shared.src.utility_dependency_checker import check_all_dependencies
from modules.shared.src.utility_llm_check import check_llm_endpoint
from modules.shared.src.utility_version import get_package_version

mcp = FastMCP("Vision")

VISION_PROJECT = str(Path(__file__).resolve().parents[3])

_dispatcher: RegistryServiceAggregate | None = None


def set_mcp_dispatcher(dispatcher: RegistryServiceAggregate | None) -> None:
    """Inject the aggregate facade used by MCP commands."""
    global _dispatcher
    _dispatcher = dispatcher


def get_dispatcher() -> RegistryServiceAggregate | None:
    """Return the injected aggregate facade if present."""
    return _dispatcher


def _execute_in_process(command: str, kwargs: dict) -> str:
    """Route command to the injected aggregate dispatcher."""
    try:
        if _dispatcher is None:
            raise RuntimeError(
                "No dispatcher configured. Call set_mcp_dispatcher() before execution."
            )
        cmd_vo = CommandName(value=command)
        return _dispatcher.execute_in_process(cmd_vo, kwargs).value
    except (KeyError, TypeError, ValueError, RuntimeError, OSError) as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def vision_init(target_dir: str = ".") -> str:
    """Initialize workspace directory structure, XDG symlinks, and SKILL.md guide."""
    return _execute_in_process("init", {"target_dir": target_dir})


@mcp.tool()
def vision_execute(
    command: str,
    video: str = "",
    image: str = "",
    image1: str = "",
    image2: str = "",
    input_path: str = "",
    output_path: str = "",
    prompt: str = "",
    lang: str = "eng",
    target_dir: str = ".",
) -> str:
    """Execute safe vision commands."""
    kwargs = {
        "image": image,
        "image1": image1,
        "image2": image2,
        "video": video,
        "input_path": input_path,
        "output_path": output_path,
        "lang": lang,
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
                "desc": "Initialize workspace with .vision-arwaky symlinks and SKILL.md",
            }
        ],
        "image": [
            {
                "command": "analyze",
                "args": "image, [prompt]",
                "desc": "Analyze screenshot or image with AI vision",
            },
            {
                "command": "ocr",
                "args": "image, [lang]",
                "desc": "Extract text from image using OCR",
            },
            {
                "command": "compare",
                "args": "image1, image2",
                "desc": "Compare two screenshots for visual differences",
            },
        ],
        "video": [
            {
                "command": "video-info",
                "args": "video",
                "desc": "Get video metadata (fps, frames, size)",
            },
            {
                "command": "extract-frames",
                "args": "video",
                "desc": "Extract frames at locked interval",
            },
            {
                "command": "check-corruption",
                "args": "video",
                "desc": "Check if video is corrupted",
            },
            {
                "command": "detect-scenes",
                "args": "video",
                "desc": "Detect scene changes",
            },
            {
                "command": "detect-motion",
                "args": "video",
                "desc": "Detect motion events",
            },
            {
                "command": "track",
                "args": "video, bbox",
                "desc": "Track object through video",
            },
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
    """Return SKILL.md documentation for vision commands."""
    skill_path = Path(VISION_PROJECT) / "SKILL.md"
    if skill_path.exists():
        content = skill_path.read_text()
    else:
        content = EMBEDDED_SKILL_MD

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
    config_path = find_active_config()
    config = load_merged_config()
    base_url, api_key, model = resolve_external_settings(config)
    selected_backend = str(config.get("backend", "external"))

    deps = check_all_dependencies()
    llm_ready, llm_status = check_llm_endpoint(
        base_url, api_key, timeout=DEFAULT_MODELS_TIMEOUT_S
    )
    deps["llm_endpoint"] = llm_status

    status_cfg: dict[str, Any] = {
        "config_yaml_detected": config_path is not None,
        "config_source": str(config_path) if config_path else "none",
        "selected_backend": selected_backend,
        "llm_endpoint": base_url,
        "llm_model": model or None,
        "llm_api_key_configured": bool(api_key),
    }

    caps = {
        "image_analysis": deps.get("opencv") == "OK",
        "ocr": deps.get("pytesseract") == "OK" and deps.get("pillow") == "OK",
        "video_processing": deps.get("opencv") == "OK" and deps.get("ffmpeg") == "OK",
        "llm_vision": llm_ready,
    }

    status: dict[str, Any] = {
        "server": f"vision-mcp v{get_package_version()}",
        "pattern": "hybrid (6 MCP tools + unlimited CLI)",
        "configuration": status_cfg,
        "dependencies": deps,
        "capabilities": caps,
    }
    return json.dumps(status, indent=2)


@mcp.tool()
def vision_cancel(job_id: str = "") -> str:
    """Cancel a running vision operation via system dispatcher."""
    return _execute_in_process("cancel", {"job_id": job_id})
