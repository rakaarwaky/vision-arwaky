import os
import logging
from src.contract import SystemUtilsPort
from src.taxonomy import BoundingBox

logger = logging.getLogger("mcp_server.infrastructure.utils")


class SystemUtilsUtil(SystemUtilsPort):
    """Concrete implementation of system utilities."""

    _taxonomy_marker = BoundingBox

    @property
    def FFMPEG_PATH(self) -> str:
        return os.environ.get("FFMPEG_PATH", "/usr/bin/ffmpeg")

    @property
    def FFPROBE_PATH(self) -> str:
        return os.environ.get("FFPROBE_PATH", "/usr/bin/ffprobe")

    def file_exists(self, path: str) -> bool:
        return os.path.exists(path)

    def get_file_size_mb(self, path: str) -> float:
        try:
            return round(os.path.getsize(path) / (1024 * 1024), 2)
        except Exception:
            return 0.0

    def validate_path(self, path: str) -> str:
        if not path:
            raise ValueError("Path empty")
        abs_p = os.path.abspath(os.path.expanduser(path))
        if not os.path.exists(abs_p):
            raise FileNotFoundError(f"Not found: {abs_p}")
        return abs_p
