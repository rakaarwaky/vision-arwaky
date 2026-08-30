"""Contract: system configuration protocol (AES402).

Pure ABC definition for loading and mutating persistent system configuration.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from modules.shared.src.taxonomy_vision_vo import ConfigKey


class SystemConfigurationProtocol(ABC):
    """Protocol for reading and mutating configuration with XDG precedence."""

    @abstractmethod
    def get_config(self, key: ConfigKey | None = None) -> Any:
        """Get the full configuration dictionary or a specific resolved key."""
        ...

    @abstractmethod
    def set_config(self, key: ConfigKey, value: Any) -> dict[str, Any]:
        """Mutate and persist a configuration key into the user XDG config file."""
        ...


__all__ = ["SystemConfigurationProtocol"]
