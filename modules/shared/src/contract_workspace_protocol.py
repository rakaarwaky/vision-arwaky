"""Contract: workspace provisioning protocol (AES402).

Pure ABC definition for workspace initialization, XDG link creation,
and embedded SKILL.md provisioning.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from modules.shared.src.taxonomy_vision_vo import FilePath


class WorkspaceProtocol(ABC):
    """Protocol for local workspace setup, XDG symlinks, and skill provisioning."""

    @abstractmethod
    def init_workspace(self, target_dir: FilePath) -> dict[str, str]:
        """Initialize workspace directory, symlinks to XDG, and SKILL.md."""
        ...


__all__ = ["WorkspaceProtocol"]
