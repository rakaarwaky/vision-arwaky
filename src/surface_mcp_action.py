"""MCP Action Surface — delegate layer for MCP tool handlers.

Mirrors lint-arwaky's McpActionSurface pattern: all MCP tools call methods
on this surface instead of routing directly in the handler.

The MCP entry point (mcp_entry.py) registers tools that delegate to
McpActionSurface methods, keeping tool registration thin.
"""

import json
import os
import shutil as _shutil
from pathlib import Path
from typing import Any

from src.image.agent_image_orchestrator import ImageOrchestrator
from src.video.agent_video_orchestrator import VideoOrchestrator
from src.memory.agent_memory_orchestrator import MemoryOrchestrator
from src.mcp.surface_mcp_handler import _check_dependencies, _check_native_vlm

VISION_PROJECT = str(Path(__file__).resolve().parents[2])

IMAGE_COMMANDS = {"analyze", "ocr", "elements", "compare"}
VIDEO_COMMANDS = {
    "video-info", "extract-frames", "convert", "check-corruption",
    "create-gif", "detect-scenes", "detect-motion", "track", "timeline",
}
MEMORY_COMMANDS = {"memory-store", "memory-search", "memory-list"}


class McpActionSurface:
    """Action surface that delegates MCP tools to feature orchestrators."""

    def __init__(self) -> None:
        self._active_processes: dict[str, Any] = {}

    # ─── Command Execution ──────────────────────────────────────────────

    def execute_command(self, command: str, kwargs: dict) -> str:
        """Route command to the appropriate feature orchestrator."""
        try:
            if command in IMAGE_COMMANDS:
                result = ImageOrchestrator.execute_image_cmd(command, kwargs)
            elif command in VIDEO_COMMANDS:
                result = VideoOrchestrator.execute_video_cmd(command, kwargs)
            elif command in MEMORY_COMMANDS:
                result = MemoryOrchestrator.execute_memory_cmd(command, kwargs)
            else:
                return json.dumps({"error": f"Unknown command: {command}"})
            return result if result is not None else json.dumps({"error": f"Command failed: {command}"})
        except Exception as e:
            return json.dumps({"error": str(e)})

    # ─── Command Discovery ──────────────────────────────────────────────

    def list_commands(self, domain: str = "") -> str:
        """List all available vision commands."""
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

    # ─── Help ──────────────────────────────────────────────────────────

    def get_help(self, section: str = "all") -> str:
        """Read SKILL.md documentation for vision commands."""
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

    # ─── Health Check ──────────────────────────────────────────────────

    def health_check(self) -> str:
        """Check vision server status, dependencies, and capabilities."""
        adapter = ImageOrchestrator.get_llm()
        project_root = Path(VISION_PROJECT)
        user_config = Path.home() / ".config" / "vision-arwaky" / "config.yaml"
        config_path = user_config if user_config.exists() else (project_root / "config.yaml")

        deps = _check_dependencies(_shutil)
        status_cfg: dict[str, Any] = {
            "config_yaml_detected": config_path.exists(),
            "config_source": "~/.config/vision-arwaky/" if user_config.exists() else "project root",
            "selected_backend": getattr(adapter, "backend", "external"),
            "native_files": {},
        }

        llm_ready = self._resolve_llm_readiness(adapter, deps, project_root, status_cfg)

        caps = {
            "image_analysis": deps.get("opencv") == "OK",
            "ocr": deps.get("pytesseract") == "OK" and deps.get("pillow") == "OK",
            "video_processing": deps.get("opencv") == "OK" and deps.get("ffmpeg") == "OK",
            "visual_memory": deps.get("opencv") == "OK",
            "llm_vision": llm_ready,
        }

        status: dict[str, Any] = {
            "server": "vision-mcp v2.0.7",
            "pattern": "AES layered (MCP tools → action surface → orchestrators)",
            "configuration": status_cfg,
            "dependencies": deps,
            "capabilities": caps,
        }
        return json.dumps(status, indent=2)

    def _resolve_llm_readiness(
        self,
        adapter: object,
        deps: dict,
        project_root: Path,
        status_cfg: dict,
    ) -> bool:
        """Determine LLM readiness and populate status config."""
        selected_backend = getattr(adapter, "backend", "external")
        adapter_config = getattr(adapter, "config", {})

        if selected_backend == "native":
            files_status, file_match = _check_native_vlm(project_root, adapter_config)
            status_cfg["native_files"] = files_status
            llm_ready = deps.get("llama-cpp-python") == "OK" and file_match
            deps["native_llm_state"] = "READY" if llm_ready else "NOT_READY"
            return llm_ready

        try:
            import requests
            DEFAULT_URL = "http://127.0.0.1:1234/v1"
            base_url = getattr(adapter, "base_url", DEFAULT_URL)
            session = requests.Session()
            session.headers.update({
                "Authorization": f"Bearer {getattr(adapter, 'api_key', '')}",
                "Content-Type": "application/json",
            })
            resp = session.get(f"{base_url}/models", timeout=5)
            session.close()
            deps["llm_endpoint"] = "OK"
            return resp.status_code == 200
        except Exception:
            deps["llm_endpoint"] = "UNREACHABLE"
            return False

    # ─── Cancellation ──────────────────────────────────────────────────

    def cancel(self, job_id: str = "") -> str:
        """Cancel a running vision operation."""
        if not job_id:
            if not self._active_processes:
                return json.dumps({"active_jobs": 0, "message": "No active jobs"})
            return json.dumps({
                "active_jobs": len(self._active_processes),
                "jobs": list(self._active_processes.keys()),
            })

        if job_id in self._active_processes:
            proc = self._active_processes.pop(job_id)
            proc.terminate()
            return json.dumps({"cancelled": job_id})
        return json.dumps({"error": f"Job {job_id} not found"})
