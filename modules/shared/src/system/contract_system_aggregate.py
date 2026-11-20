"""System-domain aggregate contract (AES101 `_aggregate`).

The single entry point over the system feature. Consumers (surface CLI,
MCP, TUI) pass a :class:`CommandName` and kwargs; the system agent
behind the aggregate dispatches to the rich protocol classes in
`contract_system_protocol.py`.
"""

from abc import ABC, abstractmethod

from modules.shared.src.common.taxonomy_vision_vo import (
    CommandName,
    CommandOutput,
    SystemCommandParams,
)


class ISystemAggregate(ABC):
    """Single entry point over the system feature."""

    @abstractmethod
    def execute_in_process(
        self,
        command: CommandName,
        kwargs: dict | SystemCommandParams,
    ) -> CommandOutput:
        """Route and execute a system command in-process; return its response."""
        ...


__all__ = ["ISystemAggregate"]

_layer_symbols = {"ISystemAggregate": ISystemAggregate}
