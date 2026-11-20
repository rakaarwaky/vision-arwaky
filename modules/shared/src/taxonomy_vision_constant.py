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

# --- Embedded SKILL.md for MCP vision_help fallback -------------------------
EMBEDDED_SKILL_MD: str = """---
name: vision-arwaky
description: Unified image and video intelligence for computer vision, OCR, video analysis, object tracking, and MCP integrations.
version: 3.0.0
---
# Vision Arwaky

Vision Arwaky is a Python computer-vision toolkit exposed through a CLI and an MCP server. It provides workspace initialization, image analysis, and bounded smart-video understanding.

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
| `va` / `vision-arwaky-cli` | Run workspace, image, and video commands |
| `vision-arwaky-mcp` | Start the MCP server over stdio                  |
| `vision-arwaky-tui` | Start the Textual configuration interface        |

Use `uv run <command>` during development when the project is managed by `uv`.

## MCP tools

The MCP server exposes six tools:


| Tool                   | Purpose                                         |
| ------------------------ | ------------------------------------------------- |
| `vision_init`          | Initialize workspace and provision XDG symlinks |
| `vision_execute`       | Execute a supported workspace, image, or video command |
| `vision_list_commands` | List supported command groups and commands      |
| `vision_help`          | Return this documentation or a selected section |
| `vision_status`        | Report dependency and model availability        |
| `vision_cancel`        | Cancel a running operation when supported       |

The MCP entry point is `modules/root_mcp_entry.py`, and the action surface is `modules/mcp/src/surface_mcp_action.py`. Command details are specified in [`modules/mcp/FRD.md`](modules/mcp/FRD.md).

## Backend and image analysis

The `image` command accepts an image path and an optional prompt. The image orchestrator uses the configured external OpenAI-compatible vision endpoint and falls back to deterministic image processing when a language-model response is unavailable.

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
  Initialize workspace directory structure (.vision-arwaky symlinks to XDG).
```

## CLI reference: image

```text
image
  --image PATH
  Analyze an image with VLM.
```

## CLI reference: video

```text
video
  --video PATH
  Analyze bounded key frames with a VLM and synthesize a short summary.
```

Smart-video analysis uses uniform sampling, caps selected frames at 12, bounds the summary prompt, handles per-frame VLM failure with fallback descriptions, and removes temporary frame files after execution.

## Configuration and system dependencies

The project reads configuration through `utility_config_handler` and adheres to the Linux XDG Base Directory specification. Keep machine-specific paths and credentials outside version control. Use `LLAMA_API_URL`, `LLAMA_API_KEY`, and `LLAMA_MODEL` for environment overrides. The standard runtime paths are:


| Resource                 | Typical location                           |
| -------------------------- | -------------------------------------------- |
| Configuration            | `~/.config/vision-arwaky/config.yaml` (`$XDG_CONFIG_HOME/vision-arwaky`) |
| User Data & Venv         | `~/.local/share/vision-arwaky` (`$XDG_DATA_HOME/vision-arwaky`) |
| Cache                    | `~/.cache/vision-arwaky` (`$XDG_CACHE_HOME/vision-arwaky`) |
| Logs & State             | `~/.local/state/vision-arwaky` (`$XDG_STATE_HOME/vision-arwaky`) |
| Executable Binaries      | `~/.local/bin` (`$XDG_BIN_HOME`) |

Required system executables are:

- `ffmpeg` and `ffprobe` for video operations.
- A working headless OpenCV runtime for image and video processing.

On Debian or Ubuntu:

```bash
sudo apt-get update
sudo apt-get install -y ffmpeg libgl1
```

## Development verification

From the repository root:

```bash
uv sync
bash scripts/gates.sh
```

The gates run Ruff formatting, Ruff lint, Mypy, pytest, and `lint-arwaky-cli scan .`. CI additionally builds the package and runs pytest on Python 3.12 and 3.13.

## Current limitations

VLM analysis requires a reachable external vision endpoint and a vision-capable model. Smart-video analysis uses a bounded representative sample rather than exhaustively sending every video frame to the VLM.
"""

__all__ = [
    "ANALYZE_VIDEO_INTERVAL_S",
    "DEFAULT_MODELS_TIMEOUT_S",
    "DEFAULT_VIDEO_FPS",
    "DEFAULT_VLM_MAX_TOKENS",
    "DEFAULT_VLM_TEMPERATURE",
    "DEFAULT_VLM_TIMEOUT_S",
    "EMBEDDED_SKILL_MD",
    "FFMPEG_TIMEOUT_S",
    "MAX_SMART_VIDEO_FRAMES",
    "MAX_SUMMARY_PROMPT_CHARS",
]
