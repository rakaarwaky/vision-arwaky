"""Package version utility."""
from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

PACKAGE_NAME = "vision-arwaky"


def get_package_version() -> str:
    """Retrieve installed package version or fallback."""
    try:
        return version(PACKAGE_NAME)
    except PackageNotFoundError:
        return "unknown"

