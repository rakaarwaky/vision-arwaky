"""Image-domain aggregate contract (AES101 `_aggregate`).

The single entry point over the image feature. Consumers (surface CLI,
MCP, TUI) pass a :class:`CommandName` and kwargs; the image agent
behind the aggregate dispatches to the rich protocol classes in
`contract_image_protocol.py`.
"""

from abc import ABC, abstractmethod

from modules.shared.src.common.taxonomy_vision_vo import (
    CommandName,
    CommandOutput,
    SystemCommandParams,
)


class IImageAggregate(ABC):
    """Single entry point over the image feature."""

    @abstractmethod
    def execute_in_process(
        self,
        command: CommandName,
        kwargs: dict | SystemCommandParams,
    ) -> CommandOutput:
        """Route and execute an image command in-process; return its response."""
        ...


__all__ = ["IImageAggregate"]

_layer_symbols = {"IImageAggregate": IImageAggregate}
