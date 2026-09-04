# Vision Arwaky — Agent Context & Operational Manual

## Concept

Unified Computer Vision & Visual Language Model (VLM) engine for local multi-agent systems. Exposes CLI, TUI, and Model Context Protocol (MCP) server for OCR, scene detection, visual analysis, and visual memory.

Adheres strictly to the **Architecture Enforcement System (AES)** 7-layer pattern for zero host contamination and high-density agent workflows.

## AES 7-Layer Pattern

Enforced by `lint-arwaky-cli`. Import rules (bottom-up):

| Layer | Purpose | Allowed Imports | Forbids |
|---|---|---|---|
| **Taxonomy** | VOs, entities, errors, constants | Taxonomy | All else |
| **Utility** | Stateless helpers | Taxonomy | Contract, Capabilities, Agent, Surface, Root |
| **Contract** | Protocol ABCs, interfaces | Taxonomy, Contract | Agent, Surface, Capabilities, Root |
| **Capabilities** | Business logic + models | Taxonomy, Contract, Utility | Agent, Surface, Root, other Capabilities |
| **Agent** | Orchestration via protocols | Taxonomy, Contract, Utility | Direct Capabilities, Surface, Root |
| **Surface** | CLI, MCP, and TUI boundaries | Taxonomy, Contract, Utility | Agent, Capabilities, Root |
| **Root** | Composition and dependency injection | All layers | None |

File naming convention: `{layer}_{concern}_{role}.{ext}`.

## Workspace Structure

```text
modules/
├── shared/src/       # taxonomy_*, contract_*, utility_*
├── core/src/         # agent_*, capabilities_*
├── cli/src/          # surface_cli_*, root_cli_*
└── mcp/src/          # surface_mcp_*, root_mcp_*
scripts/
├── install.local.sh  # Complete XDG installer
├── install.sh        # Standard entrypoint runner
├── uninstall.sh      # Clean uninstaller
└── gates.sh          # Local quality gate (ruff, mypy, pytest, AES lint)
tests/                # Unit, integration, fixtures
```

## Quickstart & Developer Workflow

```bash
# 1. Install into isolated XDG environment (~/.local/share/vision-arwaky/venv)
./scripts/install.sh

# 2. Run local quality gates before committing
bash scripts/gates.sh

# 3. Execution commands
vision-arwaky --help
vision-arwaky-cli --help
vision-arwaky-mcp
```

## Quality Gates & Verification

Before opening any PR or pushing code:
```bash
bash scripts/gates.sh
```
The script runs:
1. `ruff format --check`
2. `ruff check`
3. `mypy modules/`
4. `pytest tests/ -q`
5. `lint-arwaky-cli scan .` (Must have 0 violations)
