# Vision Arwaky

Vision Arwaky is a Python 3.12+ computer-vision MCP server for image analysis, OCR, video processing, motion and scene detection, object tracking, video timelines, and bounded smart-video understanding.

The documentation follows the relationship **PRD → FRD → README**. The PRD describes product intent for stakeholders, FRDs describe functional behavior for engineers and QA, and this README describes how developers install and operate the project.

## Quick Start

The supported development workflow uses `uv` and the package metadata in `pyproject.toml`.

```bash
# Install the project and its Python dependencies.
uv sync

# Install system dependencies on Debian or Ubuntu.
sudo apt-get update
sudo apt-get install -y ffmpeg libgl1 tesseract-ocr

# Run the CLI through the package environment.
uv run vision-arwaky-cli --help
uv run vision-arwaky-cli init
uv run vision-arwaky-cli analyze --image photo.png --prompt "Describe this scene"
uv run vision-arwaky-cli ocr --image scan.jpg
uv run vision-arwaky-cli analyze-video --video recording.mp4

# Start the MCP server over stdio.
uv run vision-arwaky-mcp

# Start the Textual configuration interface.
uv run vision-arwaky-tui
```

For an editable installation, use `uv sync` from the repository root. The package exposes the same three console scripts after installation: `vision-arwaky-cli`, `vision-arwaky-mcp`, and `vision-arwaky-tui`.

## Product and Feature Documentation

| Document | Audience | Purpose |
|---|---|---|
| [PRD.md](PRD.md) | Stakeholders, product, design, engineering | Product problem, goals, scope, requirements, metrics, and risks |
| [System FRD](modules/system/FRD.md) | Engineers and QA | Workspace initialization, XDG paths, and configuration |
| [Image FRD](modules/image/FRD.md) | Engineers and QA | Image analysis, OCR, comparison, and VLM behavior |
| [Video FRD](modules/video/FRD.md) | Engineers and QA | Video processing, analysis, tracking, and smart video |
| [CLI FRD](modules/cli/FRD.md) | Engineers and QA | Parser, command handlers, and CLI contract |
| [MCP FRD](modules/mcp/FRD.md) | Engineers and QA | MCP tools, command discovery, status, help, and cancellation |

## Architecture

The source tree is organized as feature modules. Layer identity is encoded in filenames, while dependency wiring is performed by per-module composition containers (`ImageContainer`, `VideoContainer`, `SystemContainer`).

```text
modules/
├── root_cli_entry.py                 # CLI bootstrap and argument dispatching
├── root_mcp_entry.py                 # MCP bootstrap and tool registration
├── root_tui_entry.py                 # TUI bootstrap
├── shared/                           # Taxonomy, contracts, and OpenCV pure utilities
├── image/                            # Image container, analysis, OCR, and image orchestration
├── video/                            # Video container, processing, analysis, tracking, and smart understanding
├── system/                           # System container, workspace provisioning, and configuration
├── cli/                              # CLI and TUI surfaces
└── mcp/                              # MCP controller and action surfaces

tests/                                # Focused unit and end-to-end tests
scripts/gates.sh                      # Local mirror of the CI quality gates
```

The implementation uses typed contracts and constructor injection. Each module defines its own composition root container (`ImageContainer`, `VideoContainer`, `SystemContainer`), and CLI/MCP/TUI surfaces directly delegate to the appropriate domain container on demand.


## CLI Commands

The CLI command list below is implemented by `modules/cli/src/surface_cli_controller.py` and dispatched by `modules/root_cli_entry.py`.

### Workspace commands

| Command | Main arguments | Purpose |
|---|---|---|
| `init` | `[target_dir]` (optional, default: `.`) | Initialize `.vision-arwaky` symlinks to XDG and create `.agents/skills/vision-arwaky/SKILL.md` |

### Image commands

| Command | Main arguments | Purpose |
|---|---|---|
| `analyze` | `--image`, optional `--prompt` | Analyze an image with the configured VLM and fallback behavior |
| `ocr` | `--image`, optional `--lang` | Extract text using Tesseract OCR |
| `compare` | `--image1`, `--image2` | Compare two screenshots and report differences |

### Video commands

| Command | Main arguments | Purpose |
|---|---|---|
| `video-info` | `--video` | Read video metadata |
| `extract-frames` | `--video` | Extract frames at locked interval |
| `check-corruption` | `--video` | Check whether a video can be decoded successfully |
| `detect-scenes` | `--video` | Detect scene changes |
| `detect-motion` | `--video` | Detect motion events |
| `track` | `--video`, `--bbox` | Track an object through a video |
| `analyze-video` | `--video`, optional `--prompt` | Analyze bounded key frames with a VLM and synthesize a summary |

Smart-video analysis selects scene-change, motion, and uniform samples. The implementation caps selected frames at 12, bounds the summary prompt, and removes generated frame files after the command completes.

## MCP Tools

The MCP entry point registers six tools over stdio:

| Tool | Purpose |
|---|---|
| `vision_init` | Initialize workspace directory structure and provision skill guide |
| `vision_execute` | Execute a supported workspace, image, or video command |
| `vision_list_commands` | List available workspace, image, and video commands |
| `vision_help` | Read the packaged project skill documentation |
| `vision_status` | Report dependency and capability availability |
| `vision_cancel` | Cancel a running operation when supported |

Start the server with:

```bash
uv run vision-arwaky-mcp
```

Agents can discover the current command contract through `vision_list_commands`. The MCP feature details are documented in [modules/mcp/FRD.md](modules/mcp/FRD.md).

## Configuration & XDG Standards

Configuration is loaded from the user configuration directory and the repository-local configuration file. All runtime artifacts adhere strictly to the Linux XDG Base Directory specification:

| Resource | Typical location | Environment Variable |
|---|---|---|
| Configuration | `~/.config/vision-arwaky/config.yaml` | `$XDG_CONFIG_HOME/vision-arwaky` |
| User Data & Venv | `~/.local/share/vision-arwaky` | `$XDG_DATA_HOME/vision-arwaky` |
| Cache | `~/.cache/vision-arwaky` | `$XDG_CACHE_HOME/vision-arwaky` |
| Logs & State | `~/.local/state/vision-arwaky` | `$XDG_STATE_HOME/vision-arwaky` |
| Executable Binaries | `~/.local/bin` | `$XDG_BIN_HOME` |

```yaml
backend: external
external:
  url: "http://localhost:8080/v1"
  model: "llava"
```

The external backend expects an OpenAI-compatible vision endpoint. Set credentials through `LLAMA_API_KEY` or the user-only file `~/.config/vision-arwaky/config.yaml`; never commit an API key to the repository. OCR additionally requires the `tesseract` executable, and video operations require `ffmpeg`.

## Development and Verification

Run the local mirror of the GitHub Actions gates before opening or updating a PR:

```bash
bash scripts/gates.sh
```

The script checks formatting, Ruff lint, Mypy, pytest, and the repository's `lint-arwaky-cli` scan. The current CI matrix also builds the package and runs the tests on Python 3.12 and 3.13.

Individual checks are useful during development:

```bash
uv run ruff format --check modules/ tests/
uv run ruff check modules/ tests/
uv run mypy modules/
uv run pytest tests/ -q
uv build
lint-arwaky-cli scan .
```

The test suite generates its media fixtures in CI. A local environment should have OpenCV, Tesseract, and FFmpeg available before running the complete suite.

## Contributing

Create a focused branch from the latest `main`, keep feature code behind contracts and dependency injection, update the applicable FRD when public behavior changes, and run `bash scripts/gates.sh` before opening a PR. Documentation-only changes should update the relevant PRD or FRD without modifying unrelated architecture documents.

## Key Technical Documents

| Document | Purpose |
|---|---|
| [ARCHITECTURE.md](ARCHITECTURE.md) | Current architecture and dependency rules |
| [RULES_AES.md](RULES_AES.md) | AES naming, import, role, and quality rules |
| [MIGRATION_PYTHON.md](MIGRATION_PYTHON.md) | Python migration playbook and verification workflow |
| [SKILL.md](SKILL.md) | Runtime capabilities and agent-facing command reference |
| [config.yaml](config.yaml) | Repository-local configuration defaults |
