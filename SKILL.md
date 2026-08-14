---
name: vision-arwaky
description: Unified image and video intelligence for computer vision, OCR, video analysis, object tracking, and MCP integrations.
version: 2.0.7
---

# Vision Arwaky

Vision Arwaky is a Python computer-vision toolkit exposed through a CLI and an MCP server. It provides image analysis, OCR, screenshot comparison, video processing, scene and motion detection, object tracking, agent-readable timelines, and bounded smart-video understanding.

## Documentation map

The repository uses three documentation levels with different audiences:

| Document | Audience | Focus |
|---|---|---|
| [`PRD.md`](PRD.md) | Stakeholders and product teams | Product problem, goals, scope, metrics, and risks |
| Feature `FRD.md` files | Engineers and QA | Functional requirements, contracts, edge cases, integrations, and test scenarios |
| [`README.md`](README.md) | Developers | Installation, commands, configuration, testing, and contribution workflow |

Feature FRDs are available for [image](modules/image/FRD.md), [video](modules/video/FRD.md), [OpenCV](modules/opencv/FRD.md), [CLI](modules/cli/FRD.md), and [MCP](modules/mcp/FRD.md).

## Entry points

| Command | Purpose |
|---|---|
| `vision-arwaky-cli` | Run image, video, smart-video, and test commands |
| `vision-arwaky-mcp` | Start the MCP server over stdio |
| `vision-arwaky-tui` | Start the Textual configuration interface |

Use `uv run <command>` during development when the project is managed by `uv`.

## MCP tools

The MCP server exposes five tools:

| Tool | Purpose |
|---|---|
| `vision_execute` | Execute a supported image or video command |
| `vision_list_commands` | List supported command groups and commands |
| `vision_help` | Return this documentation or a selected section |
| `vision_status` | Report dependency and model availability |
| `vision_cancel` | Cancel a running operation when supported |

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

The repository does not bundle a model. External mode requires a reachable endpoint and an appropriate vision-capable model.

## CLI reference: image

```text
analyze
  --image PATH
  --prompt TEXT (optional)
  Analyze an image or the middle frame of a supported video.

ocr
  --image PATH
  --lang CODE (optional, default: eng)
  Extract text with Tesseract OCR.

elements
  --image PATH
  Detect visual or UI elements.

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
  --interval VALUE (optional)
  Extract frames through the video processing port.

convert
  --input PATH
  --output PATH
  Convert a video from an input path to an output path.

check-corruption
  --video PATH
  Check whether a video is decodable.

create-gif
  --video PATH
  --output PATH
  --start SECONDS (optional)
  --duration SECONDS (optional)
  Create a GIF from a video segment.

detect-scenes
  --video PATH
  --threshold VALUE (optional)
  Detect scene changes.

detect-motion
  --video PATH
  --min-area PIXELS (optional)
  Detect motion events.

track
  --video PATH
  --bbox X,Y,W,H
  --max-frames COUNT (optional)
  Track an object using the configured OpenCV tracker.

timeline
  --video PATH
  --interval VALUE (optional)
  Generate a video timeline for agent consumption.

analyze-video
  --video PATH
  --prompt TEXT (optional)
  --interval FRAMES (optional, default: 30)
  --scene-threshold VALUE (optional, default: 20)
  --min-area PIXELS (optional, default: 500)
  Analyze bounded key frames with a VLM and synthesize a short summary.
```

Smart-video analysis combines scene-change, motion, and uniform sampling. It caps selected frames at 120, bounds the summary prompt, handles per-frame VLM failure with fallback descriptions, and removes temporary frame files after execution.

## Test command

```bash
vision-arwaky-cli test [--image PATH] [--verbose]
```

The command runs pytest in-process and can optionally run the image and video demonstration pipeline against generated fixtures. Install the development test dependency before invoking it.

## Configuration and system dependencies

The project reads configuration through `utility_config_handler`. Keep machine-specific paths and credentials outside version control. The standard runtime paths are:

| Resource | Typical location |
|---|---|
| User configuration | `~/.config/vision-arwaky/config.yaml` |
| Repository configuration | `./config.yaml` |
| Video tools | `ffmpeg` and `ffprobe` available on `PATH` |

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

The old visual-memory CLI and MCP commands are not part of the current public surface. Do not rely on memory-related examples from older versions of this document.
