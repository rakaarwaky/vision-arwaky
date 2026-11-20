"""Video-domain aggregate contract (AES101 `_aggregate`).

The single entry point over the video feature. Consumers (surface CLI,
MCP, TUI) pass a :class:`CommandName` and kwargs; the video agent
behind the aggregate dispatches to the rich protocol classes in
`contract_video_protocol.py`.
"""

from abc import ABC, abstractmethod

from modules.shared.src.common.taxonomy_vision_vo import (
    CommandName,
    CommandOutput,
    SystemCommandParams,
)


class IVideoAggregate(ABC):
    """Single entry point over the video feature."""

    @abstractmethod
    def execute_in_process(
        self,
        command: CommandName,
        kwargs: dict | SystemCommandParams,
    ) -> CommandOutput:
        """Route and execute a video command in-process; return its response."""
        ...


__all__ = ["IVideoAggregate"]

_layer_symbols = {"IVideoAggregate": IVideoAggregate}
