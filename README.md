# Vision Arwaky

Unified computer vision MCP server — image analysis, OCR, video processing, object tracking, and visual memory. Built with AES (Agentic Engineering System) layered architecture.

## Quick Start

```bash
# Install
./scripts/install.local.sh

# CLI mode
vision-arwaky-cli analyze --image photo.png --prompt "Describe this scene"
vision-arwaky-cli ocr --image scan.jpg
vision-arwaky-cli video-info --video recording.mp4

# MCP Server mode
vision-arwaky-mcp

# TUI Config mode
vision-arwaky-tui
```

## Architecture

```
src/
├── cli_entry.py / mcp_entry.py / tui_entry.py   ← Root entry points
├── shared/                                      ← Foundation: taxonomy + contract
├── image/                                       ← Feature: image processing
├── video/                                       ← Feature: video processing
├── tracking/                                    ← Feature: object tracking
├── memory/                                      ← Feature: visual memory
├── opencv/                                      ← Feature: shared OpenCV infra
├── system_utils/                                ← Feature: system utilities
├── cli/                                         ← Surface: CLI + TUI
└── mcp/                                         ← Surface: MCP server
```

### Layers (per feature, encoded in filename prefix)

| Prefix | Layer | Example |
|--------|-------|---------|
| `taxonomy_` | Value objects & models | `vision_models_vo.py` |
| `contract_` | Ports, Protocols, Aggregates | `image_processing_protocol.py` |
| `capabilities_` | Business logic | `image_processing_processor.py` |
| `infrastructure_` | Technology adapters | `opencv_image_adapter.py` |
| `agent_` | Orchestrators | `agent_image_orchestrator.py` |
| `surface_` | CLI/MCP/TUI interfaces | `surface_cli_handler.py` |

## CLI Commands

### Image
```
analyze   — AI visual analysis (requires LLM running)
ocr       — Extract text via Tesseract
elements  — Find UI elements (buttons, inputs)
compare   — Compare two screenshots
```

### Video
```
video-info       — Get metadata (fps, resolution, frames)
extract-frames   — Extract frames at interval
convert          — Convert format
check-corruption — Validate file integrity
create-gif       — GIF from segment
detect-scenes    — Scene change detection
detect-motion    — Motion events
track            — Object tracking via bounding box
timeline         — Agent-readable video summary
```

### Memory
```
memory store   — Store image by perceptual hash
memory search  — Find similar images
memory list    — List stored images
```

## MCP Tools (5)

| Tool | Purpose |
|------|---------|
| `vision_execute` | Execute any vision command (Hydra entry) |
| `vision_list_commands` | List available commands by domain |
| `vision_help` | Read SKILL.md documentation |
| `vision_status` | Check dependencies & capabilities |
| `vision_cancel` | Cancel running operations |

## Configuration

Priority: `~/.config/vision-arwaky/config.yaml` → `./config.yaml`

```yaml
backend: "native"     # "native" (llama-cpp-python) or "external" (API)
native:
  model_path: "models/model.gguf"
  mmproj_path: "models/mmproj.gguf"
  n_gpu_layers: -1
external:
  url: "http://localhost:8080/v1"
  model: "llava"
```

## Installation Paths

| Path | Purpose |
|------|---------|
| `~/.config/vision-arwaky/config.yaml` | Configuration |
| `~/.cache/vision-arwaky/memory/` | Visual memory cache |
| `dist/venv/` | MCP server virtualenv |

## Dependencies

- Python 3.12+
- opencv-python, pillow, numpy — image processing
- pytesseract — OCR
- ffmpeg (binary) — video processing
- llama-cpp-python — native VLM inference

## Development

```bash
# Install editable
pip install -e . --no-deps

# Run tests
uv run pytest tests/ -v

# Build MCP server
bash script/build.sh
```
