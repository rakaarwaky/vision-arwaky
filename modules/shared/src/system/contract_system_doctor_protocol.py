"""Contract: system doctor readiness protocol (AES402).

Pure ABC definition for checking system dependency and capability readiness.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from modules.shared.src.common.taxonomy_vision_vo import CommandOutput


class ISystemDoctorProtocol(ABC):
    """Protocol for reporting system dependency and capability readiness."""

    @abstractmethod
    def check_readiness(self) -> CommandOutput:
        """Inspect dependencies, endpoint connectivity, and capability readiness.

        Returns a readiness report wrapped in a :class:`CommandOutput` so the
        CLI and MCP surfaces can render it directly.
        """
        ...


__all__ = ["ISystemDoctorProtocol"]
