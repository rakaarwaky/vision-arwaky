---
trigger: always
description: "Vision Arwaky operational guide. PRD.md and ARCHITECTURE.md win on ambiguity."
---
# AGENTS — vision-arwaky

## Agent Overview

Vision Arwaky is a Python 3.12+ computer-vision toolkit exposed through a CLI, an MCP server, and a TUI. The workspace follows the AES 7-layer architecture: taxonomy, contract, utility, capabilities, agent, surface, root. Feature code lives in `modules/<feature>/src/` with layer identity encoded in filenames (`capabilities_`, `agent_`, `utility_`, `root_`); shared taxonomy, contracts, and utilities live in `modules/shared/src/`. Public behavior is defined by per-feature contracts; capability files implement protocols and are composed by per-feature orchestrators. Deterministic image and video operations stay local; vision-language analysis is an optional OpenAI-compatible external adapter.

## Runtime

| Aspect          | Detail                                                        |
|-----------------|---------------------------------------------------------------|
| Language        | Python 3.12-3.13                                              |
| Environment     | `.venv` created by `uv sync` from `pyproject.toml`            |
| Artifacts       | `.vision-arwaky/` and `.worktrees/` at repo root; never write build output to `/tmp` |
| Package Manager | `uv` with `uv.lock`                                           |
| Version Probe   | `python --version`                                            |
| Setup           | `uv sync`                                                     |
| Activation      | `uv run <command>`                                            |

## Project Structure

```text
.
├── modules/                              # Root: entry points, feature modules, shared layer
└── modules/shared/                       # Taxonomy, contracts, and OpenCV pure utilities
```

## Commands

| Category    | Command                              | Scope      | CI Gate              |
|-------------|--------------------------------------|------------|----------------------|
| Test (all)  | `uv run pytest modules/ -q`          | All        | ci.yml: test         |
| Test (unit) | `uv run pytest modules/cli/ -q`      | One unit   | ci.yml: test         |
| Test (file) | `uv run pytest modules/cli/tests/unit_cli_surface.py -q` | One file   | ci.yml: test         |
| Lint        | `uv run ruff format --check modules/` + `uv run ruff check modules/` | All        | ci.yml: lint         |
| Type Check  | `uv run mypy modules/`               | All        | ci.yml: lint         |
| Arch Scan   | `lint-arwaky-cli scan .`             | All        | ci.yml: lint         |

## Reference

| Artifact     | Purpose                                    | Link                        |
|--------------|--------------------------------------------|-----------------------------|
| README       | What the tool does, every command, install | [README.md](README.md)      |
| CONTRIBUTING | Branch, commit, and PR conventions         | [CONTRIBUTING.md](CONTRIBUTING.md) |
| ARCHITECTURE | Layer contract for every crate             | [ARCHITECTURE.md](ARCHITECTURE.md) |
| ROADMAP      | What ships next, in order                  | [ROADMAP.md](ROADMAP.md)    |
| PRD          | What the product does and why              | [PRD.md](PRD.md)            |