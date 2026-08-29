"""Locked tuning constants for the vision system.

These values are bound here to keep single vision calls predictable and bounded.
"""

from __future__ import annotations

# --- Frame extraction / uniform sampling ------------------------------------
FRAME_EXTRACTION_INTERVAL_S: float = 1.0
MAX_EXTRACT_FRAMES: int = 30

# --- Scene detection --------------------------------------------------------
SCENE_THRESHOLD: float = 30.0

# --- Motion detection -------------------------------------------------------
MIN_MOTION_AREA: int = 500

# --- Object tracking --------------------------------------------------------
MAX_TRACK_FRAMES: int = 300

# --- Smart video understanding bounds ---------------------------------------
MAX_SMART_VIDEO_FRAMES: int = 12
MAX_SUMMARY_PROMPT_CHARS: int = 12000
