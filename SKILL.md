---
name: vision
description: Unified Image & Video Intelligence — computer vision, OCR, video analysis, object tracking, and visual memory.
version: 2.0.0
---

# Vision — Unified Image & Video Intelligence

Computer vision toolkit for AI agents. Handles image analysis (now with local VLM support), OCR, video processing, object tracking, and visual memory — all running locally without cloud API calls.

## Architecture

```
MCP Layer:  5 Hydra meta-tools (token-efficient)
CLI Layer:  14 commands (unlimited, zero token cost)
VLM Layer:  Local LLM adapter (LM Studio, Ollama, vLLM) for AI image understanding
SKILL.md:   This file (discovery layer)
```

## MCP Tools (5 Hydra)

| Tool | Purpose |
|------|---------|
| `vision_execute` | Execute ANY vision command (main entry point) |
| `vision_list_commands` | List available commands by domain |
| `vision_help` | Read SKILL.md documentation |
| `vision_status` | Check dependencies and capabilities |
| `vision_cancel` | Cancel running operations |

## VLM / Local LLM Image Analysis 

The `analyze` command now supports open-ended visual questions via a local vision-capable LLM. When a `prompt` is provided, the server sends the image + prompt to your local LLM endpoint. If the LLM is unavailable, it gracefully falls back to OCR + UI element detection.

### Configuration

Set environment variables before running:

```bash
export LM_STUDIO_URL="http://127.0.0.1:1234/v1"   # OpenAI-compatible endpoint
export LM_STUDIO_MODEL="qwopus3.5-9b-v3@q6_k"      # Optional: specific model
export LM_STUDIO_API_KEY="lm-studio"               # Optional: api key
```

Or pass inline:
```bash
LM_STUDIO_URL=http://localhost:11434/v1 LM_STUDIO_MODEL=llava vision analyze --image photo.png --prompt "Describe this scene"
```

### Supported Backends
- **LM Studio** — load any vision-capable GGUF model, enable server, use default URL
- **Ollama** — `ollama run llava`, set `LM_STUDIO_URL=http://localhost:11434/v1`
- **vLLM** — any OpenAI-compatible vision endpoint

### CLI Usage

```bash
# AI-powered visual analysis (requires local VLM running)
vision analyze --image clothing.png --prompt "Describe colors, patterns, and fabric style"

# Fallback analysis (OCR + elements) when no prompt given or LLM unreachable
vision analyze --image screenshot.png
```

### MCP Usage

```
# Ask a visual question
vision_execute(
    command="analyze",
    image="/path/to/photo.png",
    prompt="What objects are in this image and what are their colors?"
)

# Returns when LLM available:
# {
#   "source": "llm",
#   "text": "detailed description...",
#   "model": "qwopus3.5-9b-v3@q6_k",
#   "elements": [],
#   "error": null
# }

# Returns when LLM unavailable (fallback):
# {
#   "source": "opencv",
#   "text": "OCR text...",
#   "elements": [{"label":"ui_element","bbox":{...}}],
#   "error": "Local LLM server not reachable..."
# }
```

## CLI Commands (14)

### Image Analysis

```bash
# AI visual analysis with local VLM (requires LLM endpoint + vision model)
vision analyze --image photo.png --prompt "Describe the clothing design"

# Fallback: OCR + UI element detection (no LLM required)
vision analyze --image screenshot.png

# Extract text via OCR (English default, supports any Tesseract lang)
vision ocr --image scan.jpg
vision ocr --image scan.jpg --lang ind   # Indonesian

# Find UI elements (buttons, inputs, etc)
vision elements --image screenshot.png

# Compare two screenshots, find differences
vision compare --image1 before.png --image2 after.png
```

### Video Processing

```bash
# Get video metadata (fps, frame count, resolution)
vision video-info --video recording.mp4

# Extract frames at interval (default: 1 per second)
vision extract-frames --video recording.mp4
vision extract-frames --video recording.mp4 --interval 0.5

# Convert video format
vision convert --input recording.mov --output recording.mp4

# Check if video is corrupted
vision check-corruption --video recording.mp4

# Create GIF from video segment
vision create-gif --video recording.mp4 --output clip.gif --start 10 --duration 5
```

### Video Analysis

```bash
# Detect scene changes (threshold: 0-100, default 30)
vision detect-scenes --video recording.mp4
vision detect-scenes --video recording.mp4 --threshold 50

# Detect motion events (min-area: pixel area, default 500)
vision detect-motion --video recording.mp4
vision detect-motion --video recording.mp4 --min-area 1000

# Track object through video (bbox: X,Y,W,H)
vision track --video recording.mp4 --bbox 100,50,200,150
vision track --video recording.mp4 --bbox 100,50,200,150 --max-frames 500

# Generate agent-readable video timeline
vision timeline --video recording.mp4
vision timeline --video recording.mp4 --interval 10
```

### Visual Memory

```bash
# Store image with label
vision memory store --image logo.png --label "company logo"

# Find similar images by perceptual hash
vision memory search --query unknown.png
vision memory search --query unknown.png --max-distance 10

# List all stored images
vision memory list
```

## MCP Usage Examples

### Via vision_execute (Hydra)

```
# AI visual analysis with custom prompt
vision_execute(command="analyze", image="/path/to/screenshot.png", prompt="What UI components do you see?")

# Fallback analysis (no prompt = OCR + elements)
vision_execute(command="analyze", image="/path/to/screenshot.png")

# OCR text extraction
vision_execute(command="ocr", image="/path/to/scan.jpg", lang="ind")

# Compare images
vision_execute(command="compare", image1="/path/to/before.png", image2="/path/to/after.png")

# Video scene detection
vision_execute(command="detect-scenes", video="/path/to/video.mp4", threshold=40.0)

# Track object
vision_execute(command="track", video="/path/to/video.mp4", bbox="100,50,200,150")

# Store in visual memory
vision_execute(command="memory-store", image="/path/to/photo.png", label="my photo")

# Find similar images
vision_execute(command="memory-search", query="/path/to/query.png", max_distance=10)
```

### Via vision_list_commands

```
# List all commands
vision_list_commands()

# List only image commands
vision_list_commands(domain="image")

# List only video commands
vision_list_commands(domain="video")
```

## Common Workflows

### AI Visual Analysis (VLM)
```
1. Ensure LM Studio / Ollama is running with a vision model loaded
2. vision_execute(
     command="analyze",
     image="design.png",
     prompt="Describe colors, patterns, and materials in detail"
   )
3. Returns: {source: "llm", text: "detailed analysis...", model: "..."}
4. If LLM unreachable: auto-fallback to {source: "opencv", text: "...", error: "..."}
```

### Screenshot Comparison (before/after)
```
1. vision_execute(command="compare", image1="before.png", image2="after.png")
2. Returns: {identical, differences: [{x,y,width,height}], phash_diff}
3. If not identical: vision_execute(command="analyze", image="after.png")
```

### Video Content Summary
```
1. vision_execute(command="video-info", video="recording.mp4")
2. vision_execute(command="detect-scenes", video="recording.mp4")
3. vision_execute(command="timeline", video="recording.mp4", interval=5)
4. For each key frame: vision_execute(command="analyze", image=frame_path)
```

### OCR Document Processing
```
1. vision_execute(command="ocr", image="document.jpg", lang="eng")
2. Returns: extracted text string
3. Process text with LLM for structured data extraction
```

### Visual Search (find duplicates)
```
1. vision_execute(command="memory-store", image="photo1.png", label="vacation")
2. vision_execute(command="memory-store", image="photo2.png", label="work")
3. vision_execute(command="memory-search", query="unknown.png", max_distance=15)
4. Returns: similar images sorted by hamming distance
```

### Object Tracking in Video
```
1. vision_execute(command="extract-frames", video="surveillance.mp4", interval=1.0)
2. vision_execute(command="analyze", image="frame_0001.jpg")
3. Identify target bbox from analysis
4. vision_execute(command="track", video="surveillance.mp4", bbox="100,50,200,150")
5. Returns: list of bounding boxes showing object movement
```

## Dependencies

| Package | Purpose | Required |
|---------|---------|----------|
| opencv-contrib-python-headless | Image/video processing | Yes |
| pillow | Image I/O | Yes |
| numpy | Array operations | Yes |
| requests | HTTP client for LLM adapter | Yes |
| pytesseract | OCR text extraction | Optional |
| ffmpeg (binary) | Video conversion, GIF | Optional |
| Local LLM endpoint | VLM image analysis | Optional (LM Studio / Ollama / vLLM) |

## Limitations

- OCR requires Tesseract binary installed (`apt install tesseract-ocr`)
- Video operations require FFmpeg binary (`apt install ffmpeg`)
- Object tracking uses OpenCV KCF/CSRT (not deep learning)
- Visual memory uses perceptual hash (not neural embeddings)
- VLM analysis requires a running local LLM server with a vision-capable model
- LLM fallback to OCR occurs automatically if the endpoint is unreachable

## Status Check

```
vision_status() → returns dependency status for all capabilities
```

The status response now includes:
- `dependencies`: opencv, pillow, numpy, pytesseract, ffmpeg, requests
- `capabilities`: image_analysis, ocr, video_processing, visual_memory, **llm_vision**
- `llm_vision` indicates whether a local LLM endpoint is reachable and ready for VLM analysis
