---
name: vision-arwaky
description: Unified Image & Video Intelligence — computer vision, OCR, video analysis, object tracking, and visual memory.
version: 2.0.0
---

# Vision Arwaky — Unified Image & Video Intelligence

Computer vision toolkit for AI agents. Handles image analysis (now with local VLM support), OCR, video processing, object tracking, and visual memory — all running locally without cloud API calls.

## Architecture

```
CLI Layer:  15 commands (analyze, ocr, video-info, extract-frames, etc.)
MCP Layer:  5 Hydra meta-tools (vision_execute, vision_help, etc.)
TUI Layer:  Textual-based config manager (vision-arwaky-tui)
VLM Layer:  Local LLM adapter for AI image understanding
SKILL.md:   This file (discovery layer)
```

## Entry Points

| Command | Purpose |
|---------|---------|
| `vision-arwaky-cli` | CLI interface — all commands |
| `vision-arwaky-mcp` | MCP server for AI agents |
| `vision-arwaky-tui` | Textual-based config & system management |

## MCP Tools (5 Hydra)

| Tool | Purpose |
|------|---------|
| `vision_execute` | Execute ANY vision command (main entry) |
| `vision_list_commands` | List available commands by domain |
| `vision_help` | Read this SKILL.md documentation |
| `vision_status` | Check dependencies and capabilities |
| `vision_cancel` | Cancel running operations |

## VLM / Local LLM Image Analysis

The `analyze` command sends an image + prompt to the local LLM endpoint.
If LLM unavailable, falls back to OCR + UI element detection.

**Supports:** any OpenAI-compatible API (llama-server, LM Studio, Ollama, vLLM)
or native llama-cpp-python in-process.

### Configuration

```yaml
backend: "native"  # "native" (llama-cpp-python) or "external" (API server)
native:
  model_path: "models/model.gguf"
  mmproj_path: "models/mmproj.gguf"
  n_gpu_layers: -1
external:
  url: "http://localhost:8080/v1"
```

### Bundled ROCm binary

If `llama-server-rocm/llama-server` exists, native mode auto-spawns it as
subprocess with ROCm GPU acceleration — no manual server setup needed.

## CLI Usage — Image

```
analyze — AI visual analysis (image or video)
  args: --image, [--prompt]
  output: {"source": "llm"|"opencv", "text": "...", "model": "..."}
  note: If --image is a video (.mp4/.mov/.avi/.mkv), automatically extracts
  the middle frame and analyzes it.

ocr — Extract text via Tesseract OCR
  args: --image, [--lang] (default: eng)
  output: plain text

elements — Find UI elements (buttons, inputs, etc.)
  args: --image
  output: [{"label": "ui_element", "bbox": {...}}, ...]

compare — Compare two screenshots, find differences
  args: --image1, --image2
  output: {"identical": bool, "differences": [...], "phash_diff": bool}
```

## CLI Usage — Video

```
video-info — Get video metadata
  args: --video
  output: {"fps": 30.0, "frame_count": 353, "width": 720, "height": 1280}
  note: Duration can be calculated as frame_count / fps

extract-frames — Extract frames at interval
  args: --video, [--interval] (default: 1.0 second)
  output: ["/path/to/video_frame_0001.jpg", ...]
  IMPORTANT: Frames are saved in the SAME directory as the source video,
  with naming pattern: {video_filename}_frame_%04d.jpg

convert — Convert video format
  args: --input, --output
  output: {"success": true|false}

check-corruption — Check if video file is corrupted
  args: --video
  output: {"corrupted": true|false}

create-gif — Create GIF from video segment
  args: --video, --output, [--start], [--duration]
  output: {"success": true|false}

detect-scenes — Detect scene changes via histogram comparison
  args: --video, [--threshold] (0-100, default: 30)
  output: [{"timestamp": 1.5, "score": 0.85}, ...]
  how: Converts each frame to HSV, compares color histogram correlation.
  Low correlation = scene change. Lower threshold = more sensitive.

detect-motion — Detect motion events via frame differencing
  args: --video, [--min-area] (default: 500 pixels)
  output: [{"timestamp": 2.0, "magnitude": 0.05, "direction": 45.0, "region": {...}}, ...]
  how: Frame differencing (absdiff) → binary threshold → contour detection.
  Filters out contours below min-area. Higher min-area = less sensitive.

track — Track object through video (OpenCV KCF/CSRT)
  args: --video, --bbox (X,Y,W,H), [--max-frames] (default: 300)
  output: [{"x": 100, "y": 50, "width": 200, "height": 150}, ...]

timeline — Generate agent-readable video timeline
  args: --video, [--interval] (default: 5 seconds)
  output: {"video_path": "...", "total_frames": 353, "fps": 30.0, "key_frames": [...]}

memory — Visual memory operations
  subcommands:
    store   — Store image by perceptual hash. args: --image, --label
    search  — Find similar images. args: --query, [--max-distance]
    list    — List all stored images
```

## CLI Usage — Test

```
test — Run test suite + AI vision analysis
  args: [--image], [--verbose]
  Runs pytest on tests/, then analyzes test.jpeg with VLM,
  then analyzes test.mp4 using smart sampling pipeline:
    1. Scene detection — frame pada scene change
    2. Motion detection — frame dengan motion tertinggi
    3. Uniform sampling — tiap 30 frame
  Output: JSON with video metadata, per-frame analyses, and summary
```

## Dependencies

| Package | Purpose | Required |
|---------|---------|----------|
| opencv-contrib-python-headless | Image/video processing | Yes |
| pillow | Image I/O | Yes |
| numpy | Array operations | Yes |
| requests | HTTP client for LLM adapter | Yes |
| pytesseract | OCR text extraction | Yes |
| ffmpeg (binary) | Video conversion, GIF | Yes |
| llama-cpp-python | Native VLM inference | Yes |
| textual | TUI framework | Yes |

## Limitations

- OCR requires Tesseract binary installed (`dnf install tesseract`)
- Video operations require FFmpeg binary (`dnf install ffmpeg`)
- Object tracking uses OpenCV KCF/CSRT (not deep learning)
- Visual memory uses perceptual hash (not neural embeddings)
- VLM analysis requires a running local LLM server with a vision-capable model
- LLM fallback to OCR occurs automatically if the endpoint is unreachable
