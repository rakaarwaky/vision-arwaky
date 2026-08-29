"""XDG Base Directory paths (taxonomy layer).

Linux XDG standard paths for Vision Arwaky.
"""

from __future__ import annotations

import os
from pathlib import Path

# App name for XDG
APP_NAME = "vision-arwaky"


def _get_xdg_dir(env_var: str, default_subdir: str) -> Path:
    """Get XDG directory from env var or default."""
    env_value = os.environ.get(env_var)
    if env_value:
        return Path(env_value)
    return Path.home() / default_subdir


class XDGPaths:
    """Linux XDG Base Directory specification paths."""

    @staticmethod
    def config_dir() -> Path:
        """~/.config/vision-arwaky/ - Configuration files."""
        return _get_xdg_dir("XDG_CONFIG_HOME", ".config") / APP_NAME

    @staticmethod
    def data_dir() -> Path:
        """~/.local/share/vision-arwaky/ - User data and runtime files."""
        return _get_xdg_dir("XDG_DATA_HOME", ".local/share") / APP_NAME

    @staticmethod
    def venv_dir() -> Path:
        """~/.local/share/vision-arwaky/venv/ - Isolated Python virtual environment."""
        return XDGPaths.data_dir() / "venv"

    @staticmethod
    def cache_dir() -> Path:
        """~/.cache/vision-arwaky/ - Temporary cached frames and intermediate files."""
        return _get_xdg_dir("XDG_CACHE_HOME", ".cache") / APP_NAME

    @staticmethod
    def state_dir() -> Path:
        """~/.local/state/vision-arwaky/ - Logs and run state."""
        return _get_xdg_dir("XDG_STATE_HOME", ".local/state") / APP_NAME

    @staticmethod
    def runtime_dir() -> Path:
        """$XDG_RUNTIME_DIR/vision-arwaky/ - Sockets, PID files."""
        return _get_xdg_dir("XDG_RUNTIME_DIR", ".local/run") / APP_NAME

    @staticmethod
    def bin_dir() -> Path:
        """$XDG_BIN_HOME or ~/.local/bin - Executables."""
        env_value = os.environ.get("XDG_BIN_HOME")
        if env_value:
            return Path(env_value)
        return Path.home() / ".local" / "bin"

    @staticmethod
    def ensure_dirs() -> None:
        """Create all required XDG directories."""
        for dir_fn in [
            XDGPaths.config_dir,
            XDGPaths.data_dir,
            XDGPaths.cache_dir,
            XDGPaths.state_dir,
        ]:
            dir_fn().mkdir(parents=True, exist_ok=True)


__all__ = ["APP_NAME", "XDGPaths"]
