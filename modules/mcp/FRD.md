# FRD — Model Context Protocol Integration

## System Overview

The MCP module exposes Vision Arwaky to AI agents through a FastMCP server over stdio. It provides a small, stable tool surface (6 tools) and routes command execution to the local `RootMCPDispatcher` in `root_mcp_entry.py`. The MCP surface is an adapter that delegates pure domain execution to orchestrators and technical checks to shared utilities.

```text
MCP client
   │
   ▼
FastMCP tools
   ├── vision_init
   ├── vision_execute
   ├── vision_list_commands
   ├── vision_help
   ├── vision_status
   └── vision_cancel
   │
   ▼
MCP action surface (`surface_mcp_action.py`)
   │
   ▼
RootMCPDispatcher (`root_mcp_entry.py`)
   ├── ImageContainer  → ImageOrchestrator
   ├── VideoContainer  → VideoOrchestrator
   └── SystemContainer → SystemOrchestrator
```

Primary implementation files are `modules/mcp/src/surface_mcp_action.py`, `modules/mcp/src/surface_mcp_controller.py` (deprecated helper), and `modules/root_mcp_entry.py`.

## Functional Requirements

### FR-MCP-001: Execute vision commands

- **Description:** Execute any supported workspace, image, or video command through the injected `RootMCPDispatcher`.
- **Input:** Command name plus command-specific paths and scalar options.
- **Output:** A JSON string containing the command result or an `error` object.
- **Business rules:** The MCP surface must not instantiate feature capabilities directly; commands are routed by domain (`CommandDomain.from_command`).
- **Edge cases:** Missing command arguments, invalid command name, missing dispatcher, unavailable external dependency, VLM failure.
- **Error handling:** Convert expected key, type, value, runtime, and OS errors into JSON error responses.

### FR-MCP-002: Initialize workspace

- **Description:** Initialize workspace with XDG symlinks and skill guide via dedicated `vision_init` tool.
- **Input:** `target_dir` (default: `.`).
- **Output:** A JSON string detailing created XDG paths, symlinks, skill guide file, and git exclusion status.
- **Business rules:** Writes embedded `SKILL.md` to `.agents/skills/vision-arwaky/SKILL.md`, configures `.vision-arwaky/` symlinks, and sets up `.git/info/exclude` (or fallback `.gitignore`).

### FR-MCP-003: Discover commands

- **Description:** Return the available workspace, image, and video command catalog for agent planning.
- **Input:** Optional `domain` filter: `workspace`, `image`, or `video`.
- **Output:** JSON array for a filtered domain or JSON object containing all domains.
- **Business rules:** The catalog must contain every public command and must not advertise removed or internal commands.
- **Edge cases:** Unknown domain, empty domain, command additions.
- **Error handling:** Unknown domains should return the full supported catalog rather than a misleading partial result.

### FR-MCP-004: Read help documentation

- **Description:** Return the agent-facing `SKILL.md` or a selected section.
- **Input:** `section` with `all`, `workspace`, `image`, or `video`.
- **Output:** Markdown text.
- **Business rules:** Help content must be read from the repository’s current `SKILL.md` with fallback to `EMBEDDED_SKILL_MD`.
- **Edge cases:** Missing file, unknown section, stale section heading.
- **Error handling:** Return a clear not-found message and list supported sections.

### FR-MCP-005: Report status

- **Description:** Report configuration, Python package, and system dependency readiness via shared utilities.
- **Input:** None.
- **Output:** JSON or structured status text.
- **Business rules:** Must report reachable external endpoint via `utility_llm_check`, detected configuration source via `utility_config_handler`, and system binary presence via `utility_dependency_checker`.
- **Edge cases:** Unreachable local endpoint, non-standard configuration locations, missing system binaries.
- **Error handling:** Return structured degraded-state payload instead of raising an uncaught exception.

### FR-MCP-006: Cancel running operations

- **Description:** Report active operations and allow cancellation when background jobs are registered.
- **Input:** Optional `job_id`.
- **Output:** JSON response containing active job count or cancellation confirmation.
- **Business rules:** Synchronous handlers must return a clean response indicating zero cancellable background tasks.
- **Edge cases:** Non-existent job ID.
- **Error handling:** Return structured JSON describing unsupported or missing jobs.
