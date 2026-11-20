"""Locked tuning constants for the vision system.

These values are bound here to keep single vision calls predictable and bounded.
"""

from __future__ import annotations

# --- Smart video understanding bounds ---------------------------------------
MAX_SMART_VIDEO_FRAMES: int = 12
MAX_SUMMARY_PROMPT_CHARS: int = 12000
ANALYZE_VIDEO_INTERVAL_S: float = 30.0
DEFAULT_VIDEO_FPS: float = 30.0

# --- VLM & timeout defaults -------------------------------------------------
DEFAULT_VLM_TIMEOUT_S: int = 120
DEFAULT_MODELS_TIMEOUT_S: int = 10
DEFAULT_VLM_TEMPERATURE: float = 0.4
DEFAULT_VLM_MAX_TOKENS: int = 2048
FFMPEG_TIMEOUT_S: float = 120.0

__all__ = [
    "ANALYZE_VIDEO_INTERVAL_S",
    "DEFAULT_MODELS_TIMEOUT_S",
    "DEFAULT_VIDEO_FPS",
    "DEFAULT_VLM_MAX_TOKENS",
    "DEFAULT_VLM_TEMPERATURE",
    "DEFAULT_VLM_TIMEOUT_S",
    "FFMPEG_TIMEOUT_S",
    "MAX_SMART_VIDEO_FRAMES",
    "MAX_SUMMARY_PROMPT_CHARS",
]
