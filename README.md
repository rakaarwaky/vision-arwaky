# README — vision-arwaky

Vision Arwaky is a Python 3.12+ computer-vision toolkit that gives AI agents and developers one CLI, one MCP server, and one TUI for image analysis, OCR, screenshot comparison, video processing, scene and motion detection, object tracking, video timelines, and bounded smart-video understanding. Deterministic media operations stay local and reproducible; vision-language analysis is an optional OpenAI-compatible external adapter. The package ships typed contracts and per-feature dependency-injection containers so behavior is modular, swappable, and testable.

## Project Overview

Vision Arwaky serves AI agent developers, computer-vision developers, QA engineers, and technical maintainers who need local, scriptable access to image and video intelligence. The CLI and MCP server expose a single documented command surface for analysis, OCR, comparison, video processing, scene and motion detection, object tracking, and bounded smart-video understanding. Deterministic operations stay offline; vision-language analysis is an optional OpenAI-compatible adapter configured at runtime.

## Prerequisites

Python 3.12 or later, the `uv` package manager, and the system dependencies installed via the Quick Start commands. OCR requires the `tesseract` executable; video operations require `ffmpeg`; image decoding requires OpenCV (`libgl1`).

## Quick Start

| Step | Action | Command |
|------|--------|---------|
| 1 | Install Python dependencies | `uv sync` |
| 2 | Install system dependencies | `sudo apt-get install -y ffmpeg libgl1 tesseract-ocr` |
| 3 | Verify the CLI | `uv run vision-arwaky-cli --help` |
| 4 | Initialize a workspace | `uv run va init` |
| 5 | Analyze an image | `uv run va image photo.png` |
| 6 | Analyze another image | `uv run va image scan.jpg` |
| 7 | Analyze a video | `uv run va video recording.mp4` |
| 8 | Start the MCP server | `uv run vision-arwaky-mcp` |
| 9 | Start the TUI | `uv run vision-arwaky-tui` |

## Reference

| Artifact | Purpose | Link |
|----------|---------|------|
| PRD.md | Business goals, user stories, and scope | [PRD.md](PRD.md) |
| BACKLOG.md | What is true now, with evidence | [BACKLOG.md](BACKLOG.md) |
| ROADMAP.md | Timeline, phasing, and dependencies | [ROADMAP.md](ROADMAP.md) |
| ARCHITECTURE.md | System boundaries, tech stack, and infrastructure | [ARCHITECTURE.md](ARCHITECTURE.md) |