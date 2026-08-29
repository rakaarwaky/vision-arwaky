"""MCP controller helper (deprecated in favor of shared dependency checker)."""

from typing import Any

from modules.shared.src.utility_dependency_checker import check_all_dependencies


def _check_dependencies(_shutil: Any = None) -> dict[str, str]:
    """Helper to verify all library and binary dependencies (deprecated)."""
    return check_all_dependencies()
