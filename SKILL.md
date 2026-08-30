---
name: vision-arwaky
description: Unified image and video intelligence for computer vision, OCR, video analysis, object tracking, and MCP integrations.
version: 3.0.0
---
# Vision Arwaky

Vision Arwaky is a Python computer-vision toolkit exposed through a CLI and an MCP server. It provides workspace initialization, image analysis, OCR, screenshot comparison, video processing, scene and motion detection, object tracking, agent-readable timelines, and bounded smart-video understanding.

## Documentation map

The repository uses three documentation levels with different audiences:


| Document                 | Audience                       | Focus                                                                            |
| -------------------------- | -------------------------------- | ---------------------------------------------------------------------------------- |
| [`PRD.md`](PRD.md)       | Stakeholders and product teams | Product problem, goals, scope, metrics, and risks                                |
| Feature `FRD.md` files    | Engineers and QA               | Functional requirements, contracts, edge cases, integrations, and test scenarios |
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
| `vision_init`          | Initialize workspace directory structure and SKILL guide |
| `vision_execute`       | Execute a supported workspace, image, or video command |
| `vision_list_commands` | List supported command groups and commands      |
| `vision_help`          | Return this documentation or a selected section |
| `vision_status`        | Report dependency and model availability        |
| `vision_cancel`        | Cancel a running operation when supported       |

The MCP entry point is `modules/root_mcp_entry.py`, and the action surface is `modules/mcp/src/surface_mcp_action.py`. Command details are specified in [`modules/mcp/FRD.md`](modules/mcp/FRD.md).

## Backend and image analysis

The `analyze` command accepts an image path (or video file to extract the middle frame) and an optional prompt. The image orchestrator uses the configured external OpenAI-compatible vision endpoint and falls back to deterministic image processing when a language-model response is unavailable.

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
  Initialize .vision-arwaky symlinks to XDG and create .agents/skills/vision-arwaky/SKILL.md.
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

The project reads configuration through `utility_config_handler`. Keep machine-specific paths and credentials outside version control. Use `LLAMA_API_URL`, `LLAMA_API_KEY`, and `LLAMA_MODEL` for environment overrides. The standard runtime paths are:


| Resource                 | Typical location                           |
| -------------------------- | -------------------------------------------- |
| User configuration       | `~/.config/vision-arwaky/config.yaml`      |
| Repository configuration | `./config.yaml`                            |
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
