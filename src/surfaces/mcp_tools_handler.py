import json
import shutil as _shutil
from pathlib import Path
from typing import Any
from mcp.server.fastmcp import FastMCP
from src.contract import RegistryServiceAggregate
from .mcp_handler import _check_dependencies, _check_native_vlm
from src.taxonomy import CommandName

mcp = FastMCP("Vision")

VISION_PROJECT = str(Path(__file__).resolve().parents[2])
DEFAULT_URL = "http://127.0.0.1:1234/v1"


def _execute_in_process(command: str, kwargs: dict) -> str:
    """Execute the request using the domain capability layers directly in-process."""
    cmd_vo = CommandName(value=command)
    output_vo = RegistryServiceAggregate.get_instance().execute_in_process(cmd_vo, kwargs)
    return output_vo.value


def _resolve_llm_readiness(
    adapter: object,
    deps: dict,
    project_root: Path,
    status_cfg: dict,
) -> bool:
    """Determine LLM readiness and populate status config with native file status."""
    selected_backend = getattr(adapter, "backend", "external")
    adapter_config = getattr(adapter, "config", {})
    if selected_backend == "native":
        files_status, file_match = _check_native_vlm(project_root, adapter_config)
        status_cfg["native_files"] = files_status
        llm_ready = deps.get("llama-cpp-python") == "OK" and file_match
        deps["native_llm_state"] = "READY" if llm_ready else "NOT_READY"
        return llm_ready
    # External HTTP backend — probe the /models endpoint
    try:
        base_url = getattr(adapter, "base_url", DEFAULT_URL)
        session = getattr(adapter, "session")
        resp = session.get(f"{base_url}/models", timeout=5)
        deps["llm_endpoint"] = "OK"
        return resp.status_code == 200
    except Exception:
        deps["llm_endpoint"] = "UNREACHABLE"
        return False


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

    MEMORY COMMANDS:
      memory-store  — Store image in visual memory. Args: image, label
      memory-search — Find similar images. Args: query, [max-distance]
      memory-list   — List all stored images. Args: (none)
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
            {"command": "analyze", "args": "image, [prompt]", "desc": "Analyze screenshot for UI elements and text"},
            {"command": "ocr", "args": "image, [lang]", "desc": "Extract text from image using OCR"},
            {"command": "elements", "args": "image", "desc": "Find UI elements (buttons, inputs)"},
            {"command": "compare", "args": "image1, image2", "desc": "Compare two screenshots"},
        ],
        "video": [
            {"command": "video-info", "args": "video", "desc": "Get video metadata (fps, frames, size)"},
            {"command": "extract-frames", "args": "video, [interval]", "desc": "Extract frames at interval"},
            {"command": "convert", "args": "input_path, output_path", "desc": "Convert video format"},
            {"command": "check-corruption", "args": "video", "desc": "Check if video is corrupted"},
            {"command": "create-gif", "args": "video, output_path, [start, duration]", "desc": "Create GIF from video"},
            {"command": "detect-scenes", "args": "video, [threshold]", "desc": "Detect scene changes"},
            {"command": "detect-motion", "args": "video, [min-area]", "desc": "Detect motion events"},
            {"command": "track", "args": "video, bbox, [max-frames]", "desc": "Track object through video"},
            {"command": "timeline", "args": "video, [interval]", "desc": "Generate video timeline"},
        ],
        "memory": [
            {"command": "memory-store", "args": "image, label", "desc": "Store image in visual memory"},
            {"command": "memory-search", "args": "query, [max-distance]", "desc": "Find similar images"},
            {"command": "memory-list", "args": "(none)", "desc": "List all stored images"},
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
    adapter = RegistryServiceAggregate.get_instance().get_llm()

    project_root = Path(VISION_PROJECT)
    config_path = project_root / "config.yaml"
    deps = _check_dependencies(_shutil)
    status_cfg: dict[str, Any] = {
        "config_yaml_detected": config_path.exists(),
        "selected_backend": getattr(adapter, "backend", "external"),
        "native_files": {},
    }

    llm_ready = _resolve_llm_readiness(adapter, deps, project_root, status_cfg)

    caps = {
        "image_analysis": deps.get("opencv") == "OK",
        "ocr": deps.get("pytesseract") == "OK" and deps.get("pillow") == "OK",
        "video_processing": deps.get("opencv") == "OK" and deps.get("ffmpeg") == "OK",
        "visual_memory": deps.get("opencv") == "OK",
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
        return json.dumps({
            "active_jobs": len(_active_processes),
            "jobs": list(_active_processes.keys()),
        })

    if job_id in _active_processes:
        proc = _active_processes.pop(job_id)
        proc.terminate()
        return json.dumps({"cancelled": job_id})
    return json.dumps({"error": f"Job {job_id} not found"})
