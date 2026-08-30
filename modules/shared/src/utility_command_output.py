"""Command output serialization helper."""

from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel

from modules.shared.src.taxonomy_vision_vo import CommandOutput


def to_command_output(model: BaseModel, indent: int = 2) -> CommandOutput:
    """Serialize Pydantic model into a CommandOutput VO."""
    return CommandOutput(value=json.dumps(model.model_dump(), indent=indent))


def to_command_output_list(models: list[BaseModel], indent: int = 2) -> CommandOutput:
    """Serialize list of Pydantic models into a CommandOutput VO."""
    return CommandOutput(
        value=json.dumps([m.model_dump() for m in models], indent=indent)
    )


def dict_to_command_output(data: dict[str, Any], indent: int = 2) -> CommandOutput:
    """Serialize dictionary into a CommandOutput VO."""
    return CommandOutput(value=json.dumps(data, indent=indent))
