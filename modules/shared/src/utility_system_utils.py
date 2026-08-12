"""System utilities — stateless, pure, domain-agnostic free functions.

Module-level functions only — no classes, no state.
"""

import os
import shutil


def _resolve_binary(env_key: str, default: str) -> str:
    """Resolve a binary path from env var, then PATH, then a default."""
    env_path = os.environ.get(env_key)
    if env_path:
        return env_path
    found = shutil.which(os.path.basename(default))
    if found:
        return found
    return default


def get_ffmpeg_path() -> str:
    """Get FFmpeg binary path from environment, PATH, or default location."""
    return _resolve_binary("FFMPEG_PATH", "/usr/bin/ffmpeg")


def get_ffprobe_path() -> str:
    """Get FFprobe binary path from environment, PATH, or default location."""
    return _resolve_binary("FFPROBE_PATH", "/usr/bin/ffprobe")


def file_exists(path: str) -> bool:
    """Check if file exists at the specified path."""
    return os.path.exists(path)


def get_file_size_mb(path: str) -> float:
    """Calculate file size in megabytes (MB)."""
    try:
        return round(os.path.getsize(path) / (1024 * 1024), 2)
    except OSError:
        return 0.0


def validate_path(path: str) -> str:
    """Validate and expand path to absolute path."""
    if not path:
        raise ValueError("Path empty")
    abs_p = os.path.abspath(os.path.expanduser(path))
    if not os.path.exists(abs_p):
        raise FileNotFoundError(f"Not found: {abs_p}")
    return abs_p
