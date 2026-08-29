"""Locked tuning constants for the video domain.

These values are intentionally **not** exposed through the MCP tools or CLI
arguments.  Sampling / detection knobs let an AI agent dictate how much CPU or
how many VLM inferences get run per call, so they are bound here to keep a
single Vision call bounded regardless of how the caller phrases its request.

Keeping them as named constants (rather than magic numbers) makes the
hard-coded behaviour auditable and easy to adjust as a team.
"""

from __future__ import annotations

# --- Frame extraction / uniform sampling ------------------------------------
#: Interval (in seconds) between uniformly-sampled key-frames.
FRAME_EXTRACTION_INTERVAL_S: float = 1.0
#: Maximum number of frames to extract for a single ``extract-frames`` call.
MAX_EXTRACT_FRAMES: int = 30

# --- Scene detection --------------------------------------------------------
#: Histogram-correlation distance threshold (0-100) above which a frame is
#: treated as a scene change.
SCENE_THRESHOLD: float = 30.0

# --- Motion detection -------------------------------------------------------
#: Minimum contour area (in pixels) for a frame-difference blob to count as
#: a motion event.
MIN_MOTION_AREA: int = 500

# --- Object tracking --------------------------------------------------------
#: Default maximum number of frames to track an object through.
MAX_TRACK_FRAMES: int = 300