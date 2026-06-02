import asyncio
from typing import List
from src.contract import VideoProcessingProtocol
from src.contract import OpenCVImagePort
from src.contract import FFmpegVideoPort
from src.taxonomy import VideoTimeline, FilePath, TimeSegment, IntervalSeconds, VideoInfo


class VideoProcessingProcessor(VideoProcessingProtocol):
    """Capability for extracting frames, converting video formats, and generating GIFs."""

    def __init__(self, opencv_port: OpenCVImagePort, ffmpeg_port: FFmpegVideoPort):
        _ = VideoTimeline
        self._opencv = opencv_port
        self._ffmpeg = ffmpeg_port

    async def extract_frames(self, video_path: FilePath, interval: IntervalSeconds) -> List[FilePath]:
        """Extract frames from video at specific interval."""
        import os
        import glob
        output_pattern = f"{video_path.value}_frame_%04d.jpg"
        # Remove stale frames first
        for stale in glob.glob(output_pattern.replace("%04d", "*")):
            os.remove(stale)

        # ffmpeg -i input -vf fps=1/interval output_%04d.jpg
        cmd = ["ffmpeg", "-i", video_path.value, "-vf", f"fps=1/{interval.value}", "-y", output_pattern]
        process = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        if process.returncode != 0:
            raise RuntimeError(f"FFmpeg extract-frames failed: {stderr.decode()[:500]}")
        # Return ACTUAL files that exist on disk — never mock
        extracted = sorted(glob.glob(output_pattern.replace("%04d", "*")))
        return [FilePath(value=path) for path in extracted]

    async def convert_format(self, input_path: FilePath, output_path: FilePath) -> bool:
        """Convert video format using FFmpeg."""
        return await self._ffmpeg.convert_video(input_path, output_path)

    async def create_gif(
        self,
        video_path: FilePath,
        output_path: FilePath,
        segment: TimeSegment,
    ) -> bool:
        """Create high-quality GIF from video segment."""
        return await self._ffmpeg.create_gif(video_path, output_path, segment)

    def get_info(self, video_path: FilePath) -> VideoInfo:
        """Get video metadata using OpenCV."""
        cap = self._opencv.get_video_capture(video_path.value)
        if not cap.isOpened():
            raise ValueError(f"Failed to open video file: {video_path.value}")

        fps = float(cap.get(self._opencv.cv2.CAP_PROP_FPS))
        frame_count = int(cap.get(self._opencv.cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(self._opencv.cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(self._opencv.cv2.CAP_PROP_FRAME_HEIGHT))
        cap.release()

        return VideoInfo(
            fps=fps,
            frame_count=frame_count,
            width=width,
            height=height,
        )

    def check_corruption(self, video_path: FilePath) -> bool:
        """Check if video file is corrupted."""
        cap = self._opencv.get_video_capture(video_path.value)
        ret = cap.isOpened()
        if ret:
            # Check if first frame can be read
            success, _ = cap.read()
            ret = success
        cap.release()
        return not ret
