from abc import ABC, abstractmethod
from src.shared.vision_models_vo import FilePath, TimeSegment


class FFmpegVideoPort(ABC):
    """Abstract port defining FFmpeg video conversion and GIF creation services."""

    @abstractmethod
    async def run(self, args, capture_output = True):
        """Run FFmpeg command asynchronously with given arguments."""
        pass

    @abstractmethod
    def get_default_gif_args(
        self,
        input_path: FilePath,
        output_path: FilePath,
        segment: TimeSegment,
    ):
        """Get standard FFmpeg arguments for high-quality GIF creation."""
        pass

    @abstractmethod
    async def convert_video(self, input_path: FilePath, output_path: FilePath):
        """Convert video from one format to another."""
        pass

    @abstractmethod
    async def create_gif(
        self,
        input_path: FilePath,
        output_path: FilePath,
        segment: TimeSegment,
    ):
        """Create GIF from video segment."""
        pass
