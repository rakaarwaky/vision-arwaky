# FRD — Model Context Protocol Integration

## Reference

- Product requirements: [PRD.md](../../PRD.md)
- Feature backlog: [BACKLOG.md](BACKLOG.md)

## System Overview

The MCP module exposes Vision Arwaky to AI agents through a server reached over stdio. It offers a small, stable tool surface of six tools and routes command execution to the root dispatcher, which hands domain work to the image, video, and system orchestrators. The MCP surface is an adapter: it delegates domain execution to orchestrators and technical checks to shared utilities.

```text
MCP client
   │
   ▼
MCP tools
   ├── vision_init
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
Root dispatcher
   ├── Image  -> Image Orchestrator
   ├── Video  -> Video Orchestrator
   └── System -> System Orchestrator
```

## Functional Requirements

### FR-MCP-001: Execute vision commands

- **Description**: Execute any supported workspace, image, or video command through the injected root dispatcher.
- **Input**: Command name plus command-specific paths and scalar options.
- **Output**: A JSON string containing the command result or an `error` object.
- **Business Rules**: The MCP surface must not instantiate feature capabilities directly; commands are routed by domain through the shared command-domain classifier.
- **Edge Cases**: Missing command arguments, invalid command name, missing dispatcher, unavailable external dependency, VLM failure.
- **Error Handling**: Expected key, type, value, runtime, and operating system failures are converted into JSON error responses.

### FR-MCP-002: Initialize workspace

- **Description**: Initialize a workspace with XDG symlinks and the skill guide through the dedicated `vision_init` tool.
- **Input**: `target_dir`, defaulting to the current directory.
- **Output**: A JSON string detailing created XDG paths, symlinks, the skill guide file, and exclusion status.
- **Business Rules**: Writes the embedded skill guide to `.agents/skills/vision-arwaky/SKILL.md`, configures the `.vision-arwaky/` symlinks, and records `.vision-arwaky` and `.venv` in `.git/info/exclude` with a local ignore file as fallback.
- **Edge Cases**: Target directory absent, symlinks already present, workspace outside a repository, no isolated virtualenv.
- **Error Handling**: Filesystem failures return a JSON error object naming the path that failed.

### FR-MCP-003: Discover commands

- **Description**: Return the available workspace, image, and video command catalog for agent planning.
- **Input**: Optional `domain` filter taking `workspace`, `image`, or `video`.
- **Output**: JSON array for a filtered domain or a JSON object containing all domains.
- **Business Rules**: The catalog contains every public command and never advertises removed or internal commands.
- **Edge Cases**: Unknown domain, empty domain, command additions.
- **Error Handling**: An unknown domain returns the full supported catalog rather than a misleading partial result.

### FR-MCP-004: Read help documentation

- **Description**: Return the agent-facing skill guide, or one selected section of it.
- **Input**: `section` taking `all`, `workspace`, `image`, or `video`.
- **Output**: Markdown text.
- **Business Rules**: Help content is read from the repository's current skill guide with the embedded copy as fallback.
- **Edge Cases**: Missing guide file, unknown section, stale section heading.
- **Error Handling**: A clear not-found message is returned together with the list of supported sections.

### FR-MCP-005: Report status

- **Description**: Report configuration, package, and system dependency readiness through shared utilities.
- **Input**: None.
- **Output**: JSON or structured status text.
- **Business Rules**: Reports reachability of the external endpoint through the shared connectivity checker, the detected configuration source through the shared configuration handler, and system binary presence through the shared dependency checker.
- **Edge Cases**: Unreachable local endpoint, non-standard configuration locations, missing system binaries.
- **Error Handling**: A structured degraded-state payload is returned instead of an uncaught exception.

### FR-MCP-006: Cancel running operations

- **Description**: Report active operations and allow cancellation when background jobs are registered.
- **Input**: Optional `job_id`.
- **Output**: JSON response containing the active job count or a cancellation confirmation.
- **Business Rules**: Synchronous handlers return a clean response indicating zero cancellable background tasks.
- **Edge Cases**: Non-existent job identifier, no registered background jobs.
- **Error Handling**: Structured JSON describes unsupported or missing jobs.

## API Contract

### Protocol API

| Method | Input | Output | Error | Event | Description |
|--------|-------|--------|-------|-------|-------------|
| `vision_execute` | command name and command options | JSON result or JSON error object | command execution error | none | Run one supported workspace, image, or video command through the dispatcher |
| `vision_init` | `target_dir` | JSON provisioning summary | workspace provisioning error | none | Provision XDG layout, skill guide, symlinks, and exclusion entries |
| `vision_list_commands` | optional `domain` | JSON array or object of commands | domain resolution error | none | Return the public command catalog for agent planning |
| `vision_help` | `section` | Markdown text | help lookup error | none | Return the full skill guide or one section |
| `vision_status` | none | JSON or structured readiness text | readiness report error | none | Report configuration, package, and binary readiness |
| `vision_cancel` | optional `job_id` | JSON job count or cancellation confirmation | cancellation error | none | Report active operations and cancel one registered job |

### Aggregate API

| Method | Input | Output | Error | Event | Description |
|--------|-------|--------|-------|-------|-------------|
| `execute_in_process` | command name and keyword arguments | command output | command execution error | none | Single composite entry point the MCP tool surface calls to run a domain command |

## Integration Points

| System | Direction | Purpose | Failure mode |
|--------|-----------|---------|--------------|
| MCP client | in | Carry tool calls and results over the stdio transport | transport closed -> request fails, server stays up |
| Root dispatcher | out | Route every tool call to the matching domain orchestrator | dispatcher absent -> structured JSON error |
| External LLM endpoint | out | Answer image and video analysis requests | unreachable -> degraded readiness payload |
| System binaries and packages | out | Prove media and OCR tooling is available | missing -> listed as unavailable |
| Workspace filesystem | out | Write the skill guide, symlinks, and exclusion entries | permission denied -> structured JSON error |

## Non-functional Requirements

| Metric | Target | Measurement method |
|--------|--------|--------------------|
| Tool surface size | exactly six tools | tool catalog introspection |
| Tool response shape | every tool returns JSON or Markdown, never a bare exception | response audit across all tools |
| Command dispatch overhead | under 100 ms before domain work starts | timed dispatch of a no-op command |
| Readiness report latency | under 500 ms | timed readiness query |
| Error containment | zero uncaught exceptions reaching the client | fault injection on each tool |

## Test Scenarios

- Calling `vision_execute` with a valid command returns a JSON result, and with an invalid command returns a JSON `error` object.
- Calling `vision_execute` without required arguments returns a JSON error naming the missing argument.
- `vision_init` on an empty directory reports created XDG paths, symlinks, the skill guide, and exclusion status.
- `vision_list_commands` with an unknown domain returns the full supported catalog.
- `vision_help` with an unknown section returns a not-found message listing supported sections.
- `vision_status` with an unreachable endpoint returns a degraded payload instead of raising.
- `vision_cancel` with no registered jobs reports zero cancellable tasks, and with an unknown identifier describes the missing job.

## Assumptions & Constraints

- The MCP surface is an adapter: it never instantiates feature capabilities and never holds domain state.
- The tool surface stays small and stable; new capability surface is exposed through command names, not new tools.
- Synchronous handlers own no background jobs, so cancellation degrades to a zero-cancellable response.
- Help content comes from the skill guide in the repository, with the embedded copy only as fallback.

## Glossary

- **Tool**: One callable operation an MCP client discovers and invokes.
- **Dispatcher**: The root component that routes a command to the orchestrator of its domain.
- **Adapter**: A surface that translates a protocol request into calls on domain contracts without owning domain logic.
- **Degraded-state payload**: A structured answer naming what is unavailable instead of failing the request.
- **Skill guide**: The agent-facing documentation returned by the help tool.
