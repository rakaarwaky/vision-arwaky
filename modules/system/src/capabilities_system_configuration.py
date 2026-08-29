"""Capabilities: system configuration management (AES403).

Implements SystemConfigurationProtocol — reads configuration with XDG/env precedence
and overwrites/persists user settings to ~/.config/vision-arwaky/config.yaml.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from modules.shared.src.contract_system_configuration_protocol import (
    SystemConfigurationProtocol,
)
from modules.shared.src.utility_config_handler import (
    get_local_config_path,
    get_user_config_path,
    load_merged_config,
    read_yaml_config,
    save_user_config,
)


# ─── Block 1: Class Definition & Constructor ──────────────
class CapabilitiesSystemConfiguration(SystemConfigurationProtocol):
    """Manage reading, merging, and overwriting configuration files."""

    def __init__(
        self,
        config_path: Path | None = None,
        local_config_path: Path | None = None,
    ) -> None:
        """Initialize configuration capability with optional path overrides."""
        self._user_config_path = config_path or get_user_config_path()
        self._local_config_path = (
            local_config_path
            if local_config_path is not None
            else get_local_config_path()
        )

    # ─── Block 2: Public Contract (SystemConfigurationProtocol ONLY)
    def get_config(self, key: str = "") -> Any:
        """Resolve full configuration dictionary or a specific key path.

        Precedence: Environment variables > User XDG config > Local config.
        """
        data = load_merged_config(
            user_path=self._user_config_path,
            local_path=self._local_config_path,
        )
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
        user_data = read_yaml_config(self._user_config_path)

        # Apply mutation using dot-separated path
        keys = key.split(".")
        target = user_data
        for k in keys[:-1]:
            if k not in target or not isinstance(target[k], dict):
                target[k] = {}
            target = target[k]
        target[keys[-1]] = value

        # Persist to XDG config
        save_user_config(user_data, path=self._user_config_path)

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


__all__ = ["CapabilitiesSystemConfiguration"]
