"""Contract: workspace provisioning protocol (AES402).

Pure ABC definition for workspace initialization and XDG link creation.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from modules.shared.src.taxonomy_vision_vo import FilePath


class IWorkspaceProtocol(ABC):
    """Protocol for local workspace setup and XDG symlinks."""

    @abstractmethod
    def init_workspace(self, target_dir: FilePath) -> dict[str, str]:
        """Initialize workspace directory and symlinks to XDG."""
        ...


__all__ = ["IWorkspaceProtocol"]
