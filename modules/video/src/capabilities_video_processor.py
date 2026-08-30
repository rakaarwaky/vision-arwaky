from modules.shared.src.contract_ffmpeg_video_protocol import FFmpegVideoProtocol
from modules.shared.src.contract_video_processing_protocol import (
    VideoProcessingProtocol,
)
from modules.shared.src.taxonomy_vision_constant import MAX_EXTRACT_FRAMES
from modules.shared.src.taxonomy_vision_vo import (
    FilePath,
    IntervalSeconds,
    VideoInfo,
)
from modules.shared.src.utility_opencv_ops import (
    check_video_corruption,
    get_video_metadata,
)


class VideoProcessingProcessor(VideoProcessingProtocol):
    """Capability for extracting frames, checking corruption, and inspecting video metadata."""

    def __init__(self, ffmpeg_port: FFmpegVideoProtocol):
        self._ffmpeg = ffmpeg_port

    async def extract_frames(
        self, video_path: FilePath, interval: IntervalSeconds
    ) -> list[FilePath]:
        """Extract frames from video at specific interval (bounded)."""
        import glob
        import os

        output_pattern = f"{video_path.value}_frame_%04d.jpg"
        # Remove stale frames first
        for stale in glob.glob(output_pattern.replace("%04d", "*")):
            os.remove(stale)

        # ffmpeg -i input -vf fps=1/interval -frames:v MAX_EXTRACT_FRAMES output_%04d.jpg
        args = [
            "-i",
            video_path.value,
            "-vf",
            f"fps=1/{interval.value}",
            "-frames:v",
            str(MAX_EXTRACT_FRAMES),
            "-y",
            output_pattern,
        ]
        await self._ffmpeg.run(args)
        # Return ACTUAL files that exist on disk — never mock
        extracted = sorted(glob.glob(output_pattern.replace("%04d", "*")))
        return [FilePath(value=path) for path in extracted]

    def get_info(self, video_path: FilePath) -> VideoInfo:
        """Get video metadata using OpenCV utility."""
        return get_video_metadata(video_path)

    def check_corruption(self, video_path: FilePath) -> bool:
        """Check if video file is corrupted using OpenCV utility."""
        return check_video_corruption(video_path)
