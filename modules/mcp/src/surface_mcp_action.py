"""MCP surface — expose aggregate facade as MCP tools (pure delegation)."""

import json
import shutil
from pathlib import Path
from typing import Any

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
    interval: float = 1.0,
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
    """
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
    return _execute_in_process(command, kwargs)


@mcp.tool()
def vision_list_commands(domain: str = "") -> str:
    """List all available vision commands.

    Args:
        domain: Filter by domain (image, video, memory). Empty = all.
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
        ],
    }

    if domain and domain in commands:
        return json.dumps(commands[domain], indent=2)
    return json.dumps(commands, indent=2)


@mcp.tool()
def vision_help(section: str = "all") -> str:
    """Read SKILL.md documentation for vision commands.

    Args:
        section: Section to read (all, image, video, memory, workflows).
    """
    skill_path = Path(VISION_PROJECT) / "SKILL.md"
    if not skill_path.exists():
        return "SKILL.md not found. Run: vision --help"

    content = skill_path.read_text()

    if section == "all":
        return content

    sections = content.split("\n## ")
    for s in sections:
        if s.lower().startswith(section.lower()):
            return "## " + s

    return f"Section '{section}' not found. Available: all, image, video, memory, workflows"


@mcp.tool()
def vision_status() -> str:
    """Check vision server status, dependencies, and capabilities."""
    project_root = Path(VISION_PROJECT)
    user_config = Path.home() / ".config" / "vision-arwaky" / "config.yaml"
    config_path = (
        user_config if user_config.exists() else (project_root / "config.yaml")
    )
    deps = _check_dependencies(shutil)

    # Read backend from config
    selected_backend = "external"
    native_files: dict = {}
    if config_path.exists():
        try:
            with open(config_path) as f:
                cfg_data = yaml.safe_load(f)
            if not isinstance(cfg_data, dict):
                cfg_data = {}
            selected_backend = str(cfg_data.get("backend", "external"))
            native_cfg = cfg_data.get("native", {})
            if isinstance(native_cfg, dict):
                model_rel = str(native_cfg.get("model_path", "") or "")
                mmproj_rel = str(native_cfg.get("mmproj_path", "") or "")
                native_files = {
                    "model_file": "MISSING"
                    if not model_rel
                    else (
                        "FOUND" if (project_root / model_rel).exists() else "MISSING"
                    ),
                    "mmproj_file": "MISSING"
                    if not mmproj_rel
                    else (
                        "FOUND" if (project_root / mmproj_rel).exists() else "MISSING"
                    ),
                }
        except (OSError, ValueError, yaml.YAMLError) as e:
            native_files["config_error"] = str(e)

    status_cfg: dict[str, Any] = {
        "config_yaml_detected": config_path.exists(),
        "config_source": "~/.config/vision-arwaky/"
        if user_config.exists()
        else "project root",
        "selected_backend": selected_backend,
        "native_files": native_files,
    }

    # Resolve LLM readiness
    llm_ready = False
    if selected_backend == "native":
        file_match = all(v == "FOUND" for v in native_files.values())
        llm_ready = deps.get("llama-cpp-python") == "OK" and file_match
        deps["native_llm_state"] = "READY" if llm_ready else "NOT_READY"
    else:
        try:
            import requests

            base_url = DEFAULT_URL
            resp = requests.get(f"{base_url}/models", timeout=5)
            deps["llm_endpoint"] = "OK"
            llm_ready = resp.status_code == 200
        except (OSError, requests.RequestException):
            deps["llm_endpoint"] = "UNREACHABLE"

    caps = {
        "image_analysis": deps.get("opencv") == "OK",
        "ocr": deps.get("pytesseract") == "OK" and deps.get("pillow") == "OK",
        "video_processing": deps.get("opencv") == "OK" and deps.get("ffmpeg") == "OK",
        "llm_vision": llm_ready,
    }

    status: dict[str, Any] = {
        "server": "vision-mcp v2.0.4",
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
            return json.dumps({"active_jobs": 0, "message": "No active jobs"})
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
    return json.dumps({"error": f"Job {job_id} not found"})
