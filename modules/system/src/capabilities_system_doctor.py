"""Capabilities: system doctor — dependency and readiness checks (AES403).

Implements a readiness check that reports which system and Python dependencies
are available, whether the LLM endpoint is reachable, and a single boolean
summary of overall system readiness.
"""

from __future__ import annotations

from modules.shared.src.common.taxonomy_vision_constant import (
    DEFAULT_MODELS_TIMEOUT_S,
)
from modules.shared.src.common.taxonomy_vision_vo import CommandOutput
from modules.shared.src.common.utility_command_output import dict_to_command_output
from modules.shared.src.common.utility_config_handler import (
    find_active_config,
    resolve_external_settings,
)
from modules.shared.src.common.utility_dependency_checker import check_all_dependencies
from modules.shared.src.common.utility_llm_check import check_llm_endpoint
from modules.shared.src.common.utility_version_resolver import get_package_version
from modules.shared.src.system.contract_system_protocol import (
    ISystemDoctorProtocol,
)


# ─── Block 1: Module Declaration ──────────────
class CapabilitiesSystemDoctor(ISystemDoctorProtocol):
    """Doctor capability for system readiness diagnostics."""

    # ─── Block 2: Module Contract ────
    def check_readiness(self) -> CommandOutput:
        """Check all system dependencies and return a structured readiness report.

        The report is serialized into a :class:`CommandOutput` with keys:
          - ready: bool — True if all *required* checks pass
          - version: str — package version string
          - checks: dict — individual check results
            - dependencies: dict[str, str] — raw dep status (OK / MISSING)
            - llm_endpoint: dict — LLM connectivity result
            - config: dict — config file detection
            - capabilities: dict[str, bool] — derived capability flags
          - failed: list[str] — names of checks that failed
        """
        deps = check_all_dependencies()
        base_url, api_key, model = resolve_external_settings()

        llm_ready, llm_status = check_llm_endpoint(
            base_url, api_key, timeout=DEFAULT_MODELS_TIMEOUT_S
        )

        config_path = find_active_config()
        pkg_version = get_package_version()

        capabilities = {
            "image_analysis": deps.get("opencv") == "OK",
            "video_processing": deps.get("opencv") == "OK"
            and deps.get("ffmpeg") == "OK",
            "llm_vision": llm_ready,
        }

        failed: list[str] = []
        for name, val in capabilities.items():
            if not val:
                failed.append(name)
        if not llm_ready:
            failed.append("llm_endpoint")

        report = {
            "ready": not failed,
            "version": f"vision-arwaky v{pkg_version}",
            "checks": {
                "dependencies": deps,
                "llm_endpoint": llm_status,
                "config": {
                    "config_yaml_detected": config_path is not None,
                    "config_source": str(config_path) if config_path else "none",
                    "llm_endpoint": base_url,
                    "llm_model": model or None,
                    "llm_api_key_configured": bool(api_key),
                },
                "capabilities": capabilities,
            },
            "failed": failed,
        }
        return dict_to_command_output(report)

    # ─── Block 3: Module Helpers ─────────
    def __repr__(self) -> str:
        return "CapabilitiesSystemDoctor()"


__all__ = ["CapabilitiesSystemDoctor"]
