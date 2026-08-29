"""Capabilities: system configuration management (AES403).

Implements SystemConfigurationProtocol — reads configuration with XDG/env precedence
and overwrites/persists user settings to ~/.config/vision-arwaky/config.yaml.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

from modules.shared.src.contract_system_configuration_protocol import (
    SystemConfigurationProtocol,
)
from modules.shared.src.taxonomy_xdg_paths_vo import XDGPaths


# ─── Block 1: Class Definition & Constructor ──────────────
class CapabilitiesSystemConfiguration(SystemConfigurationProtocol):
    """Manage reading, merging, and overwriting configuration files."""

    def __init__(
        self,
        config_path: Path | None = None,
        local_config_path: Path | None = None,
    ) -> None:
        """Initialize configuration capability with optional path overrides."""
        self._user_config_path = config_path or (XDGPaths.config_dir() / "config.yaml")
        self._local_config_path = (
            local_config_path
            if local_config_path is not None
            else Path.cwd() / "config.yaml"
        )

    # ─── Block 2: Public Contract (SystemConfigurationProtocol ONLY)
    def get_config(self, key: str = "") -> Any:
        """Resolve full configuration dictionary or a specific key path.

        Precedence: Environment variables > User XDG config > Local config.
        """
        data = self._load_merged_data()
        if not key:
            return data

        keys = key.split(".")
        current: Any = data
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return None
        return current

    def set_config(self, key: str, value: Any) -> dict[str, Any]:
        """Mutate and persist key-value pair into the user XDG config file."""
        user_data = self._read_yaml(self._user_config_path)

        # Apply mutation using dot-separated path
        keys = key.split(".")
        target = user_data
        for k in keys[:-1]:
            if k not in target or not isinstance(target[k], dict):
                target[k] = {}
            target = target[k]
        target[keys[-1]] = value

        # Persist to XDG config
        self._user_config_path.parent.mkdir(parents=True, exist_ok=True)
        with self._user_config_path.open("w", encoding="utf-8") as f:
            yaml.safe_dump(user_data, f, default_flow_style=False)

        return {
            "status": "updated",
            "path": str(self._user_config_path),
            "key": key,
            "value": value,
            "config": self.get_config(),
        }

    # ─── Block 3: Dunder Methods, Factories & Helpers ─────────
    def __repr__(self) -> str:
        return f"CapabilitiesSystemConfiguration(path={self._user_config_path})"

    def _read_yaml(self, path: Path) -> dict[str, Any]:
        """Safely read YAML dictionary from path."""
        if not path.exists():
            return {}
        try:
            with path.open("r", encoding="utf-8") as f:
                content = yaml.safe_load(f)
            return content if isinstance(content, dict) else {}
        except (OSError, yaml.YAMLError):
            return {}

    def _load_merged_data(self) -> dict[str, Any]:
        """Merge local fallback, user XDG config, and environment overrides."""
        local = self._read_yaml(self._local_config_path)
        user = self._read_yaml(self._user_config_path)

        merged: dict[str, Any] = {**local, **user}
        if "external" in local and "external" in user:
            merged["external"] = {**local["external"], **user["external"]}

        # Environment variable overrides
        if os.getenv("LLAMA_API_URL"):
            merged.setdefault("external", {})["url"] = os.getenv("LLAMA_API_URL")
        if os.getenv("LLAMA_API_KEY"):
            merged.setdefault("external", {})["api_key"] = os.getenv("LLAMA_API_KEY")
        if os.getenv("LLAMA_MODEL"):
            merged.setdefault("external", {})["model"] = os.getenv("LLAMA_MODEL")

        return merged


__all__ = ["CapabilitiesSystemConfiguration"]
