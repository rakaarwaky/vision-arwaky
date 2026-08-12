import asyncio
import logging

from modules.shared.src.contract_ffmpeg_video_protocol import FFmpegVideoProtocol
from modules.shared.src.taxonomy_vision_models_vo import (
    FilePath,
    TimeSegment,
    VideoTimeline,
)
from modules.shared.src.utility_system_utils import get_ffmpeg_path

logger = logging.getLogger("mcp_server.infrastructure.ffmpeg")


class FFmpegVideoAdapter(FFmpegVideoProtocol):
    """Infrastructure adapter for FFmpeg operations."""

    _taxonomy_marker = VideoTimeline

    async def run(self, args: list[str], capture_output: bool = True) -> str:
        ffmpeg_path = get_ffmpeg_path()
        # Convert any potential path or environment string

        full_args = [ffmpeg_path, *args]
        logger.info(f"Running ffmpeg: {' '.join(full_args)}")

        proc = await asyncio.create_subprocess_exec(
            *full_args,
            stdout=asyncio.subprocess.PIPE if capture_output else None,
            stderr=asyncio.subprocess.PIPE if capture_output else None,
        )
        stdout, stderr = await proc.communicate()

        if proc.returncode != 0:
            err_msg = stderr.decode() if stderr else "Unknown error"
            logger.error(f"FFmpeg failed with code {proc.returncode}: {err_msg}")
            raise RuntimeError(f"FFmpeg error: {err_msg}")

        return stdout.decode() if stdout else ""

    def get_default_gif_args(
        self,
        input_path: FilePath,
        output_path: FilePath,
        segment: TimeSegment,
    ) -> list[str]:
        args = []
        if segment.start is not None:
            args.extend(["-ss", str(segment.start)])
        if segment.duration is not None:
            args.extend(["-t", str(segment.duration)])
        args.extend(
            [
                "-i",
                input_path.value,
                "-vf",
                "fps=10,scale=480:-1:flags=lanczos",
                "-y",
                output_path.value,
            ]
        )
        return args

    async def convert_video(self, input_path: FilePath, output_path: FilePath) -> bool:
        """Convert video from one format to another."""
        args = ["-i", input_path.value, "-y", output_path.value]
        await self.run(args)
        return True

    async def create_gif(
        self,
        input_path: FilePath,
        output_path: FilePath,
        segment: TimeSegment,
    ) -> bool:
        """Create GIF from video segment."""
        args = self.get_default_gif_args(input_path, output_path, segment)
        await self.run(args)
        return True
