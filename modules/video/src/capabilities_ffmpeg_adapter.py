import asyncio
import logging

from modules.shared.src.contract_ffmpeg_video_protocol import FFmpegVideoProtocol
from modules.shared.src.taxonomy_vision_models_vo import VideoInfo
from modules.shared.src.utility_system_utils import get_ffmpeg_path

logger = logging.getLogger("mcp_server.infrastructure.ffmpeg")
FFMPEG_TIMEOUT_SECONDS = 120.0


class FFmpegVideoAdapter(FFmpegVideoProtocol):
    """Infrastructure adapter for FFmpeg operations."""

    _taxonomy_marker = VideoInfo

    async def run(
        self,
        args: list[str],
        capture_output: bool = True,
        timeout: float = FFMPEG_TIMEOUT_SECONDS,
    ) -> str:
        """Run FFmpeg with bounded execution and no interactive stdin."""
        if timeout <= 0:
            raise ValueError("FFmpeg timeout must be greater than zero")

        ffmpeg_path = get_ffmpeg_path()
        full_args = [ffmpeg_path, *args]
        logger.info("Running ffmpeg: %s", " ".join(full_args))

        proc = await asyncio.create_subprocess_exec(
            *full_args,
            stdin=asyncio.subprocess.DEVNULL,
            stdout=asyncio.subprocess.PIPE if capture_output else None,
            stderr=asyncio.subprocess.PIPE if capture_output else None,
        )
        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        except TimeoutError as exc:
            proc.kill()
            await proc.wait()
            raise RuntimeError(f"FFmpeg timed out after {timeout:g}s") from exc
        except asyncio.CancelledError:
            proc.kill()
            await proc.wait()
            raise

        if proc.returncode != 0:
            err_msg = stderr.decode() if stderr else "Unknown error"
            logger.error("FFmpeg failed with code %s: %s", proc.returncode, err_msg)
            raise RuntimeError(f"FFmpeg error: {err_msg}")

        return stdout.decode() if stdout else ""

