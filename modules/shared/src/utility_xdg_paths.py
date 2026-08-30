"""XDG directory bootstrap utilities — stateless standalone functions."""

from __future__ import annotations

from modules.shared.src.taxonomy_xdg_paths_vo import XDGPaths


def ensure_xdg_dirs() -> None:
    """Create all required XDG directories."""
    for dir_fn in (
        XDGPaths.config_dir,
        XDGPaths.data_dir,
        XDGPaths.cache_dir,
        XDGPaths.state_dir,
    ):
        dir_fn().mkdir(parents=True, exist_ok=True)


__all__ = ["ensure_xdg_dirs"]
