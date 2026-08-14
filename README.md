# Vision Arwaky

Vision Arwaky is a Python 3.12+ computer-vision MCP server for image analysis, OCR, video processing, motion and scene detection, object tracking, and agent-readable video timelines. The project uses a seven-layer Agentic Engineering System (AES) architecture with dependency injection at the composition root.

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
uv run vision-arwaky-cli analyze --image photo.png --prompt "Describe this scene"
uv run vision-arwaky-cli ocr --image scan.jpg

# Start the MCP server over stdio.
uv run vision-arwaky-mcp

# Start the Textual configuration interface.
uv run vision-arwaky-tui
```

For an editable installation, use `uv sync` from the repository root. The package exposes the same three console scripts after installation: `vision-arwaky-cli`, `vision-arwaky-mcp`, and `vision-arwaky-tui`.

## Architecture

The source tree is organized as feature modules. Layer identity is encoded in filenames, while dependency wiring is performed by the root composition containers.

```text
modules/
├── root_cli_entry.py                 # CLI bootstrap and dispatcher wiring
├── root_mcp_entry.py                 # MCP bootstrap and tool registration
├── root_tui_entry.py                 # TUI bootstrap
├── root_composition_container.py     # Application-wide dependency graph
├── shared/                           # Taxonomy, contracts, and shared utilities
├── image/                            # Image analysis, OCR, and image orchestration
├── video/                            # Video processing, analysis, tracking, and timelines
├── opencv/                           # OpenCV capability adapters
├── cli/                              # CLI and TUI surfaces
└── mcp/                              # MCP controller and action surfaces

tests/                                # Integration and feature tests
scripts/gates.sh                      # Local mirror of the CI quality gates
```

### AES layers

| Filename prefix | Layer | Responsibility |
|---|---|---|
| `taxonomy_` | Taxonomy | Value objects, entities, errors, events, and constants |
| `contract_` | Contract | Protocols and aggregate facades |
| `utility_` | Utility | Stateless technical helpers |
| `capabilities_` | Capabilities | Concrete processing and infrastructure adapters |
| `agent_` | Agent | Constructor-injected feature orchestrators |
| `surface_` | Surface | CLI, MCP, and TUI interaction boundaries |
| `root_` | Root | Composition containers and application entry points |

Surfaces delegate through the injected `RegistryServiceAggregate`; they do not construct capabilities or implement domain workflows. The root layer is the only place that assembles the concrete dependency graph.

## CLI Commands

The CLI command list below is implemented by `modules/cli/src/surface_cli_controller.py` and dispatched by `modules/root_cli_entry.py`.

### Image commands

| Command | Main arguments | Purpose |
|---|---|---|
| `analyze` | `--image`, optional `--prompt` | Analyze an image with the configured VLM, with an OpenCV fallback |
| `ocr` | `--image`, optional `--lang` | Extract text using Tesseract OCR |
| `elements` | `--image` | Detect visual or UI elements |
| `compare` | `--image1`, `--image2` | Compare two screenshots and report differences |

### Video commands

| Command | Main arguments | Purpose |
|---|---|---|
| `video-info` | `--video` | Read video metadata |
| `extract-frames` | `--video`, optional interval | Extract frames through the video processing port |
| `convert` | input and output paths | Convert a video to another format |
| `check-corruption` | `--video` | Check whether a video can be decoded successfully |
| `create-gif` | video, output, start, duration | Create a GIF from a video segment |
| `detect-scenes` | `--video`, optional threshold | Detect scene changes |
| `detect-motion` | `--video`, optional minimum area | Detect motion events |
| `track` | `--video`, bounding box, optional maximum frames | Track an object through a video |
| `timeline` | `--video`, optional interval | Generate an agent-readable video timeline |

### Test command

```bash
uv run vision-arwaky-cli test [--image PATH] [--verbose]
```

The command runs pytest in-process and, when fixtures are available, performs the optional image and video analysis demonstration. It requires the test dependency to be installed in the active environment.

> The old `memory` CLI has been removed. Visual-memory commands should not be added to new integrations unless the feature is reintroduced as a complete AES slice.

## MCP Tools

The MCP entry point registers five tools over stdio:

| Tool | Purpose |
|---|---|
| `vision_execute` | Execute a supported image or video command |
| `vision_list_commands` | List the available command groups and commands |
| `vision_help` | Read the packaged project skill documentation |
| `vision_status` | Report dependency and capability availability |
| `vision_cancel` | Cancel a running operation when supported |

Start the server with:

```bash
uv run vision-arwaky-mcp
```

## Configuration

Configuration is loaded from the user configuration directory and the repository-local configuration file. The exact precedence is handled by `utility_config_handler`; keep secrets and machine-specific model paths outside version control.

```yaml
backend: external
external:
  url: "http://localhost:8080/v1"
  model: "llava"
```

The external backend expects an OpenAI-compatible vision endpoint. OCR additionally requires the `tesseract` executable, and video operations require `ffmpeg`.

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
uv run python3 -m pytest tests/ -q
uv build
lint-arwaky-cli scan .
```

The test suite generates its media fixtures in CI. A local environment should have OpenCV, Tesseract, and FFmpeg available before running the complete suite.

## Key Documents

| Document | Purpose |
|---|---|
| [ARCHITECTURE.md](ARCHITECTURE.md) | Current seven-layer architecture and dependency rules |
| [RULES_AES.md](RULES_AES.md) | AES naming, import, role, and quality rules |
| [MIGRATION_PYTHON.md](MIGRATION_PYTHON.md) | Python migration playbook and verification workflow |
| [SKILL.md](SKILL.md) | Runtime capabilities and agent-facing command reference |
| [config.yaml](config.yaml) | Repository-local configuration defaults |
