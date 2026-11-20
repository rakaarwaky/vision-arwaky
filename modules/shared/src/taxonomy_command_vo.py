"""Command domain value objects and classification."""

from __future__ import annotations

from enum import Enum

IMAGE_COMMANDS: frozenset[str] = frozenset({"image", "analyze"})

VIDEO_COMMANDS: frozenset[str] = frozenset({"video", "analyze-video"})

SYSTEM_COMMANDS: frozenset[str] = frozenset({"init", "doctor"})

ALL_COMMANDS: frozenset[str] = IMAGE_COMMANDS | VIDEO_COMMANDS | SYSTEM_COMMANDS


class CommandDomain(str, Enum):
    """Enumeration of system domains for command routing."""

    IMAGE = "image"
    VIDEO = "video"
    SYSTEM = "system"

    @classmethod
    def from_command(cls, command: str) -> CommandDomain:
        """Resolve domain enum from command name."""
        if command in IMAGE_COMMANDS:
            return cls.IMAGE
        if command in VIDEO_COMMANDS:
            return cls.VIDEO
        if command in SYSTEM_COMMANDS:
            return cls.SYSTEM
        raise ValueError(f"Unknown command: {command}")
