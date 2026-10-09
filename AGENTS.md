---
trigger: always
description: "Vision Arwaky operational guide. PRD.md and ARCHITECTURE.md win on ambiguity."
---
# Vision Arwaky

## Runtime

- Language: Python 3.12-3.13
- Environment: `.venv` created by `uv sync` from `pyproject.toml`
- Artifacts: `.vision-arwaky/` and `.worktrees/` at repo root; never write build output to `/tmp`
- Package manager: `uv` with `uv.lock`

```bash
python --version
uv sync
```

## Project Quick Facts

INPUT  = image or video file path (local, XDG-supported).
OUTPUT = JSON-structured analysis: OCR text, scene/motion events, and VLM summaries.

## Pipeline

Workspace init → Frame/OCR extraction → VLM analysis → Structured JSON
Init, Extract, Analyze, Deliver.

## Project Structure

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
```

## Commands

Every command must match the exact CI gate.

```bash
# Tests
uv run pytest modules/ -q                              # full test suite
uv run pytest modules/cli/ -q                           # one unit
uv run pytest modules/cli/tests/unit_cli_surface.py -q  # one file

# Lint / types / architecture
uv run ruff format --check modules/                    # matches ci.yml "format"
uv run ruff check modules/                             # matches ci.yml "lint"
uv run mypy modules/                                   # matches ci.yml "lint"
lint-arwaky-cli scan .                                 # self-lint, must be 0
```

## Related Documents

- [PRD.md](PRD.md): product problem, goals, scope, and requirements
- [ARCHITECTURE.md](ARCHITECTURE.md): AES 7-layer rules and module organization
- [RULES_AES.md](RULES_AES.md): AES naming, import, role, and quality rules
- [README.md](README.md): install, commands, and developer quickstart

---
