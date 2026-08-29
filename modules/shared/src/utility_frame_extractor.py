"""Frame extraction utility — stateless video frame extraction."""
from __future__ import annotations

import os
import tempfile

import cv2

from modules.shared.src.utility_opencv_ops import open_video_capture


def extract_middle_frame(video_path: str) -> str | None:
    """Extract middle frame from video to a temporary image file."""
    cap = open_video_capture(video_path)
    try:
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if total <= 0:
            return None
        cap.set(cv2.CAP_PROP_POS_FRAMES, total // 2)
        ret, frame = cap.read()
        if not ret:
            return None
        fd, thumb = tempfile.mkstemp(suffix=".jpg")
        os.close(fd)
        if not cv2.imwrite(thumb, frame):
            os.unlink(thumb)
            return None
        return thumb
    finally:
        cap.release()


def extract_frames_at_indices(
    video_path: str,
    indices: list[int],
    out_dir: str,
) -> list[tuple[int, str]]:
    """Extract frames at specified indices to a target directory."""
    extracted: list[tuple[int, str]] = []
    cap = open_video_capture(video_path)
    try:
        for idx in indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ret, frame = cap.read()
            if not ret:
                continue
            out_path = os.path.join(out_dir, f"frame_{idx:06d}.jpg")
            if not cv2.imwrite(out_path, frame):
                continue
            extracted.append((idx, out_path))
    finally:
        cap.release()
    return extracted

