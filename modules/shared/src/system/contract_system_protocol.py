"""System-domain capability contracts (AES102 `_protocol`).

One file for the system feature. Each class below is one capability
seam: a class carries every method that capability implements, with one
concrete return type each, so a capability implements its class outright
and never carries stubs.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from modules.shared.src.common.taxonomy_vision_vo import (
    CommandOutput,
    ConfigKey,
    FilePath,
)


class ISystemConfigurationProtocol(ABC):
    """System configuration capability: read and mutate persistent settings."""

    @abstractmethod
    def get_config(self, key: ConfigKey | None = None) -> Any:
        """Get the full configuration dictionary or a specific resolved key."""
        ...

    @abstractmethod
    def set_config(self, key: ConfigKey, value: Any) -> dict[str, Any]:
        """Mutate and persist a configuration key into the user XDG config file."""
        ...


class ISystemDoctorProtocol(ABC):
    """System doctor capability: report dependency and capability readiness."""

    @abstractmethod
    def check_readiness(self) -> CommandOutput:
        """Inspect dependencies, endpoint connectivity, and capability readiness."""
        ...


class ISystemJobProtocol(ABC):
    """System job capability: monitor status and cancel in-flight operations."""

    @abstractmethod
    def get_status(self) -> dict[str, Any]:
        """Inspect dependencies, endpoint connectivity, and server capability status."""
        ...

    @abstractmethod
    def cancel_job(self, job_id: CommandOutput | str = "") -> dict[str, Any]:
        """Cancel a running operation or list active jobs."""
        ...


class IWorkspaceProtocol(ABC):
    """Workspace provisioning capability: initialize workspace and XDG symlinks."""

    @abstractmethod
    def init_workspace(self, target_dir: FilePath) -> dict[str, str]:
        """Initialize workspace directory and symlinks to XDG."""
        ...


__all__ = [
    "ISystemConfigurationProtocol",
    "ISystemDoctorProtocol",
    "ISystemJobProtocol",
    "IWorkspaceProtocol",
]

_layer_symbols = {
    "ISystemConfigurationProtocol": ISystemConfigurationProtocol,
    "ISystemDoctorProtocol": ISystemDoctorProtocol,
    "ISystemJobProtocol": ISystemJobProtocol,
    "IWorkspaceProtocol": IWorkspaceProtocol,
}
