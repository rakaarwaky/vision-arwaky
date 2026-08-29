"""Contract: system job and lifecycle protocol (AES402).

Pure ABC definition for process tracking, status monitoring, and job cancellation.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class SystemJobProtocol(ABC):
    """Protocol for monitoring system status and cancelling in-flight operations."""

    @abstractmethod
    def get_status(self) -> dict[str, Any]:
        """Inspect dependencies, endpoint connectivity, and server capability status."""
        ...

    @abstractmethod
    def cancel_job(self, job_id: Any = "") -> dict[str, Any]:
        """Cancel a running operation or list active jobs."""
        ...


__all__ = ["SystemJobProtocol"]
