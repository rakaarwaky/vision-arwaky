from abc import ABC, abstractmethod

from modules.shared.src.taxonomy_vision_constant import FFMPEG_TIMEOUT_S


class FFmpegVideoProtocol(ABC):
    """Abstract port defining FFmpeg execution services."""

    @abstractmethod
    async def run(
        self,
        args: list[str],
        capture_output: bool = True,
        timeout_s: float = FFMPEG_TIMEOUT_S,
    ) -> str:
        """Run FFmpeg command asynchronously with given arguments."""
