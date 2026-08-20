"""MCP surface — expose aggregate facade as MCP tools (pure delegation)."""

import json
import os
import shutil
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

import requests
import yaml
from mcp.server.fastmcp import FastMCP

from modules.shared.src.contract_registry_service_aggregate import (
    RegistryServiceAggregate,
)
from modules.shared.src.taxonomy_vision_models_vo import CommandName

from .surface_mcp_controller import _check_dependencies

mcp = FastMCP("Vision")

VISION_PROJECT = str(Path(__file__).resolve().parents[3])
DEFAULT_URL = "http://127.0.0.1:1234/v1"

_dispatcher: RegistryServiceAggregate | None = None


def set_mcp_dispatcher(dispatcher: RegistryServiceAggregate) -> None:
    """Inject the aggregate facade used by all MCP commands."""
    global _dispatcher
    _dispatcher = dispatcher


def get_dispatcher() -> RegistryServiceAggregate:
    """Return the injected aggregate facade."""
    if _dispatcher is None:
        raise RuntimeError(
            "No dispatcher injected. Call set_mcp_dispatcher() before running commands."
        )
    return _dispatcher


def _execute_in_process(command: str, kwargs: dict) -> str:
    """Route command to the appropriate feature orchestrator via the facade."""
    try:
        result = get_dispatcher().execute_in_process(CommandName(value=command), kwargs)
        return result.value
    except (KeyError, TypeError, ValueError, RuntimeError, OSError) as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
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
    interval: float | None = None,
    scene_threshold: float | None = None,
    start: float = 0.0,
    duration: float = 0.0,
    label: str = "",
    query: str = "",
    max_distance: int = 15,
) -> str:
    """Execute ANY vision command. Available commands:

    IMAGE COMMANDS:
      analyze      — Analyze screenshot for UI elements. Args: image, [prompt]
      ocr          — Extract text via OCR. Args: image, [lang]
      elements     — Find UI elements. Args: image
      compare      — Compare two images. Args: image1, image2

    VIDEO COMMANDS:
      video-info   — Get video metadata. Args: video
      extract-frames — Extract frames. Args: video, [interval]
      convert      — Convert video format. Args: input_path, output_path
      check-corruption — Check if video corrupted. Args: video
      create-gif   — Create GIF from video. Args: video, output_path, [start, duration]
      detect-scenes — Detect scene changes. Args: video, [threshold]
      detect-motion — Detect motion events. Args: video, [min_area]
      track        — Track object. Args: video, bbox(X,Y,W,H), [max-frames]
      timeline     — Generate video timeline. Args: video, [interval]
      analyze-video — Smart video understanding. Args: video, [prompt, interval, scene_threshold, min_area]
    """
    effective_interval = (
        interval
        if interval is not None
        else (30.0 if command == "analyze-video" else 1.0)
    )
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
        "scene_threshold": (scene_threshold if scene_threshold is not None else 20.0),
        "min_area": min_area,
        "bbox": bbox,
        "max_frames": max_frames,
        "interval": effective_interval,
        "start": start,
        "duration": duration,
        "label": label,
        "query": query,
        "max_distance": max_distance,
    }
    return _execute_in_process(command, kwargs)


@mcp.tool()
def vision_list_commands(domain: str = "") -> str:
    """List all available vision commands.

    Args:
        domain: Filter by domain (image, video). Empty = all.
    """
    commands = {
        "image": [
            {
                "command": "analyze",
                "args": "image, [prompt]",
                "desc": "Analyze screenshot for UI elements and text",
            },
            {
                "command": "ocr",
                "args": "image, [lang]",
                "desc": "Extract text from image using OCR",
            },
            {
                "command": "elements",
                "args": "image",
                "desc": "Find UI elements (buttons, inputs)",
            },
            {
                "command": "compare",
                "args": "image1, image2",
                "desc": "Compare two screenshots",
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
                "args": "video, [interval]",
                "desc": "Extract frames at interval",
            },
            {
                "command": "convert",
                "args": "input_path, output_path",
                "desc": "Convert video format",
            },
            {
                "command": "check-corruption",
                "args": "video",
                "desc": "Check if video is corrupted",
            },
            {
                "command": "create-gif",
                "args": "video, output_path, [start, duration]",
                "desc": "Create GIF from video",
            },
            {
                "command": "detect-scenes",
                "args": "video, [threshold]",
                "desc": "Detect scene changes",
            },
            {
                "command": "detect-motion",
                "args": "video, [min-area]",
                "desc": "Detect motion events",
            },
            {
                "command": "track",
                "args": "video, bbox, [max-frames]",
                "desc": "Track object through video",
            },
            {
                "command": "timeline",
                "args": "video, [interval]",
                "desc": "Generate video timeline",
            },
            {
                "command": "analyze-video",
                "args": "video, [prompt, interval, scene_threshold, min_area]",
                "desc": "Analyze sampled video frames with a VLM and summarize the video",
            },
        ],
    }

    if domain and domain in commands:
        return json.dumps(commands[domain], indent=2)
    return json.dumps(commands, indent=2)


@mcp.tool()
def vision_help(section: str = "all") -> str:
    """Read SKILL.md documentation for vision commands.

    Args:
        section: Section to read (all, image, video).
    """
    skill_path = Path(VISION_PROJECT) / "SKILL.md"
    if not skill_path.exists():
        return "SKILL.md not found. Run: vision --help"

    content = skill_path.read_text()

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

    return f"Section '{section}' not found. Available: all, image, video"


def _load_runtime_config(project_root: Path) -> tuple[Path | None, dict[str, Any]]:
    """Load the same user-first configuration used by the runtime adapter."""
    user_config = Path.home() / ".config" / "vision-arwaky" / "config.yaml"
    project_config = project_root / "config.yaml"
    config_path = user_config if user_config.exists() else project_config
    if not config_path.exists():
        return None, {}
    try:
        with config_path.open() as config_file:
            data = yaml.safe_load(config_file)
        return config_path, data if isinstance(data, dict) else {}
    except (OSError, yaml.YAMLError):
        return config_path, {}


def _external_settings(config: dict[str, Any]) -> tuple[str, str, str]:
    """Resolve endpoint, API key, and model using runtime precedence."""
    external = config.get("external")
    external_config = external if isinstance(external, dict) else {}
    url = (
        os.getenv("LLAMA_API_URL") or str(external_config.get("url", "")) or DEFAULT_URL
    ).rstrip("/")
    api_key = os.getenv("LLAMA_API_KEY") or str(external_config.get("api_key", ""))
    model = os.getenv("LLAMA_MODEL") or str(external_config.get("model", ""))
    return url, api_key, model


def _package_version() -> str:
    """Return the installed package version without failing source checkouts."""
    try:
        return version("vision-arwaky")
    except PackageNotFoundError:
        return "unknown"


@mcp.tool()
def vision_status() -> str:
    """Check vision server status, dependencies, and capabilities."""
    project_root = Path(VISION_PROJECT)
    config_path, config = _load_runtime_config(project_root)
    deps = _check_dependencies(shutil)
    selected_backend = str(config.get("backend", "external"))
    base_url, api_key, model = _external_settings(config)

    status_cfg: dict[str, Any] = {
        "config_yaml_detected": config_path is not None,
        "config_source": "~/.config/vision-arwaky/"
        if config_path is not None
        and config_path == Path.home() / ".config" / "vision-arwaky" / "config.yaml"
        else "project root",
        "selected_backend": selected_backend,
        "llm_endpoint": base_url,
        "llm_model": model or None,
        "llm_api_key_configured": bool(api_key),
    }

    llm_ready = False
    try:
        headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
        response = requests.get(f"{base_url}/models", headers=headers, timeout=5)
        llm_ready = 200 <= response.status_code < 300
        deps["llm_endpoint"] = "OK" if llm_ready else f"HTTP_{response.status_code}"
    except (OSError, requests.RequestException):
        deps["llm_endpoint"] = "UNREACHABLE"

    caps = {
        "image_analysis": deps.get("opencv") == "OK",
        "ocr": deps.get("pytesseract") == "OK" and deps.get("pillow") == "OK",
        "video_processing": deps.get("opencv") == "OK" and deps.get("ffmpeg") == "OK",
        "llm_vision": llm_ready,
    }

    status: dict[str, Any] = {
        "server": f"vision-mcp v{_package_version()}",
        "pattern": "hybrid (5 MCP tools + unlimited CLI)",
        "configuration": status_cfg,
        "dependencies": deps,
        "capabilities": caps,
    }
    return json.dumps(status, indent=2)


_active_processes: dict = {}


@mcp.tool()
def vision_cancel(job_id: str = "") -> str:
    """Cancel a running vision operation.

    Args:
        job_id: Job ID to cancel. Empty = list active jobs.
    """
    if not job_id:
        if not _active_processes:
            return json.dumps(
                {
                    "active_jobs": 0,
                    "supported": False,
                    "message": "Commands execute synchronously; no cancellable jobs are registered.",
                }
            )
        return json.dumps(
            {
                "active_jobs": len(_active_processes),
                "jobs": list(_active_processes.keys()),
            }
        )

    if job_id in _active_processes:
        proc = _active_processes.pop(job_id)
        proc.terminate()
        return json.dumps({"cancelled": job_id})
    return json.dumps(
        {
            "error": f"Job {job_id} not found",
            "supported": False,
            "message": "No asynchronous jobs are registered by the current MCP execution path.",
        }
    )
