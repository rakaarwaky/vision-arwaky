from abc import ABC, abstractmethod


class FFmpegVideoProtocol(ABC):
    """Abstract port defining FFmpeg execution services."""

    @abstractmethod
    async def run(
        self,
        args: list[str],
        capture_output: bool = True,
    ) -> str:
        """Run FFmpeg command asynchronously with given arguments."""
