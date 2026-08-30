"""Capabilities: system job and process lifecycle management (AES403).

Implements SystemJobProtocol — status reporting, dependency inspection, and operation cancellation.
"""

from __future__ import annotations

from typing import Any

from modules.shared.src.contract_system_job_protocol import SystemJobProtocol
from modules.shared.src.taxonomy_vision_constant import DEFAULT_MODELS_TIMEOUT_S
from modules.shared.src.utility_config_handler import (
    find_active_config,
    resolve_external_settings,
)
from modules.shared.src.utility_dependency_checker import check_all_dependencies
from modules.shared.src.utility_llm_check import check_llm_endpoint
from modules.shared.src.utility_version_resolver import get_package_version


# ─── Block 1: Class Definition & Constructor ──────────────
class CapabilitiesSystemJob(SystemJobProtocol):
    """Job tracking, lifecycle monitoring, and process cancellation."""

    def __init__(self) -> None:
        """Initialize CapabilitiesSystemJob."""

    # ─── Block 2: Public Contract (SystemJobProtocol ONLY) ────
    def get_status(self) -> dict[str, Any]:
        """Inspect dependencies, endpoint connectivity, and server capability status."""
        deps = check_all_dependencies()
        base_url, api_key, model = resolve_external_settings()

        llm_ready, llm_status = check_llm_endpoint(
            base_url, api_key, timeout=DEFAULT_MODELS_TIMEOUT_S
        )
        deps["llm_endpoint"] = llm_status

        config_path = find_active_config()
        pkg_version = get_package_version()
        return {
            "server": f"vision-mcp v{pkg_version}",
            "configuration": {
                "config_yaml_detected": config_path is not None,
                "config_source": str(config_path) if config_path else "none",
                "llm_endpoint": base_url,
                "llm_model": model or None,
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
            "active_jobs": 0,
        }

    def cancel_job(self, job_id: CommandOutput | str = "") -> dict[str, Any]:
        """Report that synchronous execution does not support cancellation."""
        return {
            "active_jobs": 0,
            "supported": False,
            "message": "Commands execute synchronously; no cancellable jobs are registered.",
        }

    # ─── Block 3: Dunder Methods, Factories & Helpers ─────────
    def __repr__(self) -> str:
        return "CapabilitiesSystemJob()"


__all__ = ["CapabilitiesSystemJob"]
