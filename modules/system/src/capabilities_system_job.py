"""Capabilities: system job and process lifecycle management (AES403).

Implements SystemJobProtocol — status reporting, dependency inspection, and operation cancellation.
"""

from __future__ import annotations

import os
import shutil
from importlib.metadata import PackageNotFoundError, version
from typing import Any

import requests

from modules.shared.src.contract_system_job_protocol import SystemJobProtocol
from modules.shared.src.taxonomy_vision_constant import DEFAULT_MODELS_TIMEOUT_S
from modules.shared.src.taxonomy_xdg_paths_vo import XDGPaths


# ─── Block 1: Class Definition & Constructor ──────────────
class CapabilitiesSystemJob(SystemJobProtocol):
    """Job tracking, lifecycle monitoring, and process cancellation."""

    def __init__(self) -> None:
        """Initialize CapabilitiesSystemJob with empty in-flight registry."""
        self._active_processes: dict[str, Any] = {}

    # ─── Block 2: Public Contract (SystemJobProtocol ONLY) ────
    def get_status(self) -> dict[str, Any]:
        """Inspect dependencies, endpoint connectivity, and server capability status."""
        deps = self._check_dependencies()
        base_url = (os.getenv("LLAMA_API_URL") or "http://127.0.0.1:1234/v1").rstrip(
            "/"
        )
        api_key = os.getenv("LLAMA_API_KEY") or ""
        model = os.getenv("LLAMA_MODEL") or None

        llm_ready = False
        try:
            headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
            response = requests.get(
                f"{base_url}/models",
                headers=headers,
                timeout=DEFAULT_MODELS_TIMEOUT_S,
            )
            llm_ready = 200 <= response.status_code < 300
            deps["llm_endpoint"] = "OK" if llm_ready else f"HTTP_{response.status_code}"
        except (OSError, requests.RequestException):
            deps["llm_endpoint"] = "UNREACHABLE"

        config_path = XDGPaths.config_dir() / "config.yaml"
        return {
            "server": f"vision-mcp v{self._package_version()}",
            "configuration": {
                "config_yaml_detected": config_path.exists(),
                "config_source": str(config_path)
                if config_path.exists()
                else "project root",
                "llm_endpoint": base_url,
                "llm_model": model,
                "llm_api_key_configured": bool(api_key),
            },
            "dependencies": deps,
            "capabilities": {
                "image_analysis": deps.get("opencv") == "OK",
                "ocr": deps.get("pytesseract") == "OK" and deps.get("pillow") == "OK",
                "video_processing": deps.get("opencv") == "OK"
                and deps.get("ffmpeg") == "OK",
                "llm_vision": llm_ready,
            },
            "active_jobs": len(self._active_processes),
        }

    def cancel_job(self, job_id: str = "") -> dict[str, Any]:
        """Cancel a running operation or report active jobs."""
        if not job_id:
            if not self._active_processes:
                return {
                    "active_jobs": 0,
                    "supported": False,
                    "message": "Commands execute synchronously; no cancellable jobs are registered.",
                }
            return {
                "active_jobs": len(self._active_processes),
                "jobs": list(self._active_processes.keys()),
            }

        if job_id in self._active_processes:
            proc = self._active_processes.pop(job_id)
            if hasattr(proc, "terminate"):
                proc.terminate()
            return {"cancelled": job_id}

        return {
            "error": f"Job {job_id} not found",
            "supported": False,
            "message": "No asynchronous jobs are registered by the current execution path.",
        }

    # ─── Block 3: Dunder Methods, Factories & Helpers ─────────
    def __repr__(self) -> str:
        return f"CapabilitiesSystemJob(active={len(self._active_processes)})"

    @staticmethod
    def _package_version() -> str:
        try:
            return version("vision-arwaky")
        except PackageNotFoundError:
            return "unknown"

    @staticmethod
    def _check_dependencies() -> dict[str, str]:
        deps: dict[str, str] = {}
        for lib in ["cv2", "PIL", "pytesseract"]:
            try:
                __import__(lib)
                deps[lib.lower().replace("cv2", "opencv")] = "OK"
            except ImportError:
                deps[lib.lower().replace("cv2", "opencv")] = "MISSING"

        for bin_name in ["ffmpeg", "ffprobe", "tesseract"]:
            deps[bin_name] = "OK" if shutil.which(bin_name) else "MISSING"

        return deps


__all__ = ["CapabilitiesSystemJob"]
