"""Locked tuning constants for the vision system.

These values are bound here to keep single vision calls predictable and bounded.
"""

from __future__ import annotations

# --- Frame extraction / uniform sampling ------------------------------------
FRAME_EXTRACTION_INTERVAL_S: float = 1.0
MAX_EXTRACT_FRAMES: int = 30

# --- Scene detection --------------------------------------------------------
SCENE_THRESHOLD: float = 30.0
HIST_HUE_BINS: int = 50
HIST_SAT_BINS: int = 60

# --- Motion detection -------------------------------------------------------
MIN_MOTION_AREA: int = 500
MOTION_DIFF_THRESHOLD: int = 25
MOTION_MAX_PIXEL_VALUE: int = 255
GAUSSIAN_BLUR_KERNEL: tuple[int, int] = (21, 21)
DILATION_KERNEL_SIZE: tuple[int, int] = (3, 3)
DILATION_ITERATIONS: int = 2

# --- Object tracking --------------------------------------------------------
MAX_TRACK_FRAMES: int = 300

# --- Smart video understanding bounds ---------------------------------------
MAX_SMART_VIDEO_FRAMES: int = 12
MAX_SUMMARY_PROMPT_CHARS: int = 12000
ANALYZE_VIDEO_INTERVAL_S: float = 30.0
TOP_MOTION_EVENTS_LIMIT: int = 5
DEFAULT_VIDEO_FPS: float = 30.0

# --- Image processing & comparison bounds -----------------------------------
IMAGE_DIFF_THRESHOLD: int = 30
IMAGE_MAX_PIXEL_VALUE: int = 255
MIN_DIFF_CONTOUR_AREA: int = 50
DEFAULT_OCR_LANGUAGE: str = "eng"

# --- VLM & FFmpeg timeout defaults ------------------------------------------
DEFAULT_VLM_TIMEOUT_S: int = 120
DEFAULT_MODELS_TIMEOUT_S: int = 10
DEFAULT_VLM_TEMPERATURE: float = 0.4
DEFAULT_VLM_MAX_TOKENS: int = 2048
FFMPEG_TIMEOUT_S: float = 120.0

# --- Embedded SKILL.md for workspace provisioning ---------------------------
EMBEDDED_SKILL_MD: str = """---
name: vision-arwaky
description: Unified image and video intelligence for computer vision, OCR, video analysis, object tracking, and MCP integrations.
version: 2.0.7
---
# Vision Arwaky

Vision Arwaky is a Python computer-vision toolkit exposed through a CLI and an MCP server. It provides workspace initialization, image analysis, OCR, screenshot comparison, video processing, scene and motion detection, object tracking, agent-readable timelines, and bounded smart-video understanding.

## Documentation map

The repository uses three documentation levels with different audiences:


| Document                 | Audience                       | Focus                                                                            |
| -------------------------- | -------------------------------- | ---------------------------------------------------------------------------------- |
| [`PRD.md`](PRD.md)       | Stakeholders and product teams | Product problem, goals, scope, metrics, and risks                                |
| Feature `FRD.md` files   | Engineers and QA               | Functional requirements, contracts, edge cases, integrations, and test scenarios |
| [`README.md`](README.md) | Developers                     | Installation, commands, configuration, testing, and contribution workflow        |

Feature FRDs are available for [shared](modules/shared/FRD.md), [system](modules/system/FRD.md), [image](modules/image/FRD.md), [video](modules/video/FRD.md), [CLI](modules/cli/FRD.md), and [MCP](modules/mcp/FRD.md).

## Entry points


| Command             | Purpose                                          |
| --------------------- | -------------------------------------------------- |
| `va` / `vision-arwaky-cli` | Run workspace, image, video, and smart-video commands |
| `vision-arwaky-mcp` | Start the MCP server over stdio                  |
| `vision-arwaky-tui` | Start the Textual configuration interface        |

Use `uv run <command>` during development when the project is managed by `uv`.

## MCP tools

The MCP server exposes six tools:


| Tool                   | Purpose                                         |
| ------------------------ | ------------------------------------------------- |
| `vision_init`          | Initialize workspace and provision skill guide  |
| `vision_execute`       | Execute a supported workspace, image, or video command |
| `vision_list_commands` | List supported command groups and commands      |
| `vision_help`          | Return this documentation or a selected section |
| `vision_status`        | Report dependency and model availability        |
| `vision_cancel`        | Cancel a running operation when supported       |

The MCP entry point is `modules/root_mcp_entry.py`, and the action surface is `modules/mcp/src/surface_mcp_action.py`. Command details are specified in [`modules/mcp/FRD.md`](modules/mcp/FRD.md).

## Backend and image analysis

The `analyze` command accepts an image path and an optional prompt. The image orchestrator uses the configured external OpenAI-compatible vision endpoint and falls back to deterministic image processing when a language-model response is unavailable.

The supported backend configuration is:

```yaml
backend: external
external:
  url: "http://localhost:8080/v1"
  model: "llava"
```

The repository does not bundle a model. External mode requires a reachable endpoint and an appropriate vision-capable model. Set credentials through `LLAMA_API_KEY` or `~/.config/vision-arwaky/config.yaml`; never commit an API key to the repository.

## CLI reference: workspace

```text
init
  [target_dir] (optional, default: .)
  Initialize workspace directory structure (.vision-arwaky symlinks to XDG and .agents/skills/vision-arwaky/SKILL.md).
```

## CLI reference: image

```text
analyze
  --image PATH
  --prompt TEXT (optional)
  Analyze an image with VLM or deterministic fallback.

ocr
  --image PATH
  --lang CODE (optional, default: eng)
  Extract text with Tesseract OCR.

compare
  --image1 PATH
  --image2 PATH
  Compare two screenshots and report perceptual differences.
```

## CLI reference: video

```text
video-info
  --video PATH
  Read video metadata.

extract-frames
  --video PATH
  Extract frames at a locked interval.

check-corruption
  --video PATH
  Check whether a video is decodable.

detect-scenes
  --video PATH
  Detect scene changes.

detect-motion
  --video PATH
  Detect motion events.

track
  --video PATH
  --bbox X,Y,W,H
  Track an object using OpenCV tracker.

analyze-video
  --video PATH
  --prompt TEXT (optional)
  Analyze bounded key frames with a VLM and synthesize a short summary.
```

Smart-video analysis combines scene-change, motion, and uniform sampling. It caps selected frames at 12, bounds the summary prompt, handles per-frame VLM failure with fallback descriptions, and removes temporary frame files after execution.

## Configuration and system dependencies

The project reads configuration through `utility_config_handler` and adheres to the Linux XDG Base Directory specification. Keep machine-specific paths and credentials outside version control. Use `LLAMA_API_URL`, `LLAMA_API_KEY`, and `LLAMA_MODEL` for environment overrides. The standard runtime paths are:


| Resource                 | Typical location                           |
| -------------------------- | -------------------------------------------- |
| Configuration            | `~/.config/vision-arwaky/config.yaml` (`$XDG_CONFIG_HOME/vision-arwaky`) |
| User Data & Venv         | `~/.local/share/vision-arwaky` (`$XDG_DATA_HOME/vision-arwaky`) |
| Cache                    | `~/.cache/vision-arwaky` (`$XDG_CACHE_HOME/vision-arwaky`) |
| Logs & State             | `~/.local/state/vision-arwaky` (`$XDG_STATE_HOME/vision-arwaky`) |
| Executable Binaries      | `~/.local/bin` (`$XDG_BIN_HOME`) |
| Video tools              | `ffmpeg` and `ffprobe` available on `PATH` |

Required system executables are:

- `tesseract` for OCR.
- `ffmpeg` and `ffprobe` for video operations.
- A working headless OpenCV runtime for image and video processing.

On Debian or Ubuntu:

```bash
sudo apt-get update
sudo apt-get install -y ffmpeg libgl1 tesseract-ocr
```

## Development verification

From the repository root:

```bash
uv sync
bash scripts/gates.sh
```

The gates run Ruff formatting, Ruff lint, Mypy, pytest, and `lint-arwaky-cli scan .`. CI additionally builds the package and runs pytest on Python 3.12 and 3.13.

## Current limitations

VLM analysis requires a reachable external vision endpoint and a vision-capable model. OCR requires the Tesseract binary. Video processing requires FFmpeg. Object tracking uses OpenCV trackers rather than a deep-learning detector. Smart-video analysis uses a bounded representative sample rather than exhaustively sending every video frame to the VLM.
"""

__all__ = [
    "ANALYZE_VIDEO_INTERVAL_S",
    "DEFAULT_MODELS_TIMEOUT_S",
    "DEFAULT_OCR_LANGUAGE",
    "DEFAULT_VIDEO_FPS",
    "DEFAULT_VLM_MAX_TOKENS",
    "DEFAULT_VLM_TEMPERATURE",
    "DEFAULT_VLM_TIMEOUT_S",
    "DILATION_ITERATIONS",
    "DILATION_KERNEL_SIZE",
    "EMBEDDED_SKILL_MD",
    "FFMPEG_TIMEOUT_S",
    "FRAME_EXTRACTION_INTERVAL_S",
    "GAUSSIAN_BLUR_KERNEL",
    "HIST_HUE_BINS",
    "HIST_SAT_BINS",
    "IMAGE_DIFF_THRESHOLD",
    "IMAGE_MAX_PIXEL_VALUE",
    "MAX_EXTRACT_FRAMES",
    "MAX_SMART_VIDEO_FRAMES",
    "MAX_SUMMARY_PROMPT_CHARS",
    "MAX_TRACK_FRAMES",
    "MIN_DIFF_CONTOUR_AREA",
    "MIN_MOTION_AREA",
    "MOTION_DIFF_THRESHOLD",
    "MOTION_MAX_PIXEL_VALUE",
    "SCENE_THRESHOLD",
    "TOP_MOTION_EVENTS_LIMIT",
]
