# FRD — Model Context Protocol Integration

## System Overview

The MCP module exposes Vision Arwaky to AI agents through a FastMCP server. It provides a small, stable tool surface and routes command execution to the same injected root dispatcher used by the CLI. The MCP layer is an adapter, not a second feature implementation.

```text
MCP client
   │
   ▼
FastMCP tools
   ├── vision_execute
   ├── vision_list_commands
   ├── vision_help
   ├── vision_status
   └── vision_cancel
   │
   ▼
MCP action surface
   │
   ▼
RootDispatcher → Image / Video graph
```

Primary implementation files are `surface_mcp_action.py`, `surface_mcp_controller.py`, and `root_mcp_entry.py`.

## Functional Requirements

### FR-MCP-001: Execute vision commands

- **Description:** Execute any supported image or video command through the injected root dispatcher.
- **Input:** Command name plus command-specific paths and scalar options.
- **Output:** A JSON string containing the command result or an `error` object.
- **Business rules:** The MCP surface must not instantiate feature capabilities directly. `analyze-video` must accept prompt, interval, scene threshold, and minimum motion area.
- **Edge cases:** Missing command arguments, invalid command name, missing dispatcher, unavailable external dependency, VLM failure.
- **Error handling:** Convert expected key, type, value, runtime, and OS errors into JSON error responses.

### FR-MCP-002: Discover commands

- **Description:** Return the available image and video command catalog for agent planning.
- **Input:** Optional `domain` filter, either `image` or `video`.
- **Output:** JSON array for a filtered domain or JSON object containing both domains.
- **Business rules:** The catalog must contain every public command, including `analyze-video`, and must not advertise removed memory commands.
- **Edge cases:** Unknown domain, empty domain, command additions.
- **Error handling:** Unknown domains should return the full supported catalog rather than a misleading partial result.

### FR-MCP-003: Read help documentation

- **Description:** Return the agent-facing `SKILL.md` or a selected image or video section.
- **Input:** `section` with `all`, `image`, or `video`.
- **Output:** Markdown text.
- **Business rules:** Help content must be read from the repository’s current `SKILL.md`.
- **Edge cases:** Missing file, unknown section, stale section heading.
- **Error handling:** Return a clear not-found message and list supported sections.

### FR-MCP-004: Report status

- **Description:** Report configuration, Python package, and system dependency readiness.
- **Input:** None.
- **Output:** JSON or structured status text.
- **Business rules:** The status result must distinguish project configuration, user configuration, Python dependencies, system binaries, configured endpoint, model, and whether a credential is present without exposing the credential.
- **Edge cases:** No config file, no VLM model, missing FFmpeg, missing Tesseract, missing OpenCV import.
- **Error handling:** Status must remain usable even when optional dependencies are unavailable.

### FR-MCP-005: Cancel active work

- **Description:** Inspect or cancel tracked asynchronous MCP jobs when an asynchronous execution controller is enabled. The current command execution path is synchronous and reports cancellation as unsupported rather than pretending that a job was cancelled.
- **Input:** Optional job identifier.
- **Output:** JSON containing active jobs, cancellation status, or an explicit `supported: false` response.
- **Business rules:** Cancelling an unknown job must not crash the server, and the current synchronous path must clearly identify that no cancellable jobs are registered.
- **Edge cases:** Empty job list, unknown identifier, already completed job.
- **Error handling:** Return a controlled error object for an unknown job.

## API Contract

| Tool | Input | Output | Description |
|---|---|---|---|
| `vision_execute` | `command` plus command arguments | JSON string | Execute image or video command |
| `vision_list_commands` | Optional `domain` | JSON catalog | Discover supported commands |
| `vision_help` | Optional `section` | Markdown string | Read agent-facing docs |
| `vision_status` | None | Status JSON or text | Check configuration and dependencies |
| `vision_cancel` | Optional `job_id` | Cancellation JSON | Inspect jobs or report current cancellation support |

Supported command groups are:

| Domain | Commands |
|---|---|
| Image | `analyze`, `ocr`, `elements`, `compare` |
| Video | `video-info`, `extract-frames`, `convert`, `check-corruption`, `create-gif`, `detect-scenes`, `detect-motion`, `track`, `timeline`, `analyze-video` |

## Integration Points

The MCP server is packaged as `vision-arwaky-mcp`. It uses FastMCP for tool registration, the root composition container for dependency injection, the project or user YAML configuration for runtime settings, and the CLI-independent dispatcher for execution.

## Non-functional Requirements

- **Agent compatibility:** Every tool must expose clear parameter names and machine-readable error responses.
- **Reliability:** A failed command must not terminate the MCP server process.
- **Discoverability:** The command catalog and help content must match the CLI and implementation.
- **Security:** MCP parameters must remain data passed to Python APIs; the server must not build shell command strings from user input.
- **Observability:** Status and command errors should identify the unavailable dependency or invalid argument.
- **Testability:** Tool functions must be testable without a running MCP transport or external VLM endpoint.

## Test Scenarios / QA Checklist

- [ ] Import the MCP entry module without starting a transport.
- [ ] Execute an invalid command and verify a JSON error.
- [ ] Execute image and video commands with missing required inputs and verify controlled errors.
- [ ] List all commands and verify image and video groups exist.
- [ ] Verify `analyze-video` appears in the video discovery list.
- [ ] Filter the command list by `image` and `video`.
- [ ] Read all help and the image/video help sections.
- [ ] Report status with and without a user configuration file.
- [ ] Verify status uses `LLAMA_API_URL`, `LLAMA_API_KEY`, and `LLAMA_MODEL` overrides without exposing the key.
- [ ] Cancel an empty job list and an unknown job identifier.
- [ ] Verify MCP commands route through the injected dispatcher.

## Assumptions and Constraints

The MCP server is intended for local or trusted environments. Authentication and multi-tenant authorization are outside the current product scope. External VLM availability is optional for deterministic commands but required for successful VLM-backed analysis.

## Reference

- [Product requirements](../../PRD.md)
- [CLI FRD](../cli/FRD.md)
- [Developer README](../../README.md)
- [Agent-facing skill](../../SKILL.md)
