from abc import ABC, abstractmethod
from typing import Any

from modules.shared.src.taxonomy_vision_vo import (
    CommandName,
    CommandOutput,
)


class RegistryServiceAggregate(ABC):
    """Facade contract for unified in-process command execution.

    Concrete per-domain agents receive their capability ports via
    constructor injection (see root containers) and implement this
    contract purely by delegation.
    """

    @abstractmethod
    def execute_in_process(
        self,
        command: CommandName,
        kwargs: dict[str, Any],
    ) -> CommandOutput:
        """Route and execute a command in-process across the domain."""
