from abc import ABC, abstractmethod

from modules.shared.src.taxonomy_vision_vo import VideoInfo


class FFmpegVideoProtocol(ABC):
    """Abstract port defining FFmpeg execution services."""

    _taxonomy_marker = VideoInfo

    @abstractmethod
    async def run(
        self,
        args: list[str],
        capture_output: bool = True,
    ) -> str:
        """Run FFmpeg command asynchronously with given arguments."""
