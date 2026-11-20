# FRD — Model Context Protocol Server

## Feature Overview

The MCP module exposes Vision Arwaky to AI agents through a stdio server offering a small, stable tool surface of six tools: vision_init, vision_execute, vision_list_commands, vision_help, vision_status, and vision_cancel. The MCP surface is an adapter: it delegates domain execution to the root dispatcher (which routes to the image, video, and system orchestrators) and technical checks to shared utilities. It never instantiates feature capabilities directly and never holds domain state.

## Functional Requirements

### FR-MCP-001: Execute vision commands

**Description:** Execute any supported workspace, image, or video command through the injected root dispatcher.

#### Business Logic

- The MCP surface must not instantiate feature capabilities directly; commands are routed by domain through the shared command-domain classifier.

#### Edge Cases

- Missing command arguments, invalid command name, missing dispatcher, unavailable external dependency, VLM failure.

#### Technical Specification

| Aspect | Detail |
|--------|--------|
| **Input** | Command name plus command-specific paths and scalar options |
| **Output** | A JSON string containing the command result or an `error` object |
| **Protocol** | stdio |
| **Method** | `vision_execute` |
| **Event** | None |
| **Error** | Expected key, type, value, runtime, and operating system failures are converted into JSON error responses |

#### Test

| Context | When Action | Then Observable Result |
|---------|-------------|------------------------|
| valid command | call vision_execute | returns a JSON result |
| invalid command | call vision_execute | returns a JSON `error` object |
| missing required arguments | call vision_execute | returns a JSON error naming the missing argument |

#### Metric

| Target Metric | Value |
|---------------|-------|
| Command dispatch overhead | under 100 ms before domain work starts |

### FR-MCP-002: Initialize workspace

**Description:** Initialize a workspace with XDG symlinks through the dedicated `vision_init` tool.

#### Business Logic

- Configures the `.vision-arwaky/` symlinks.
- Records `.vision-arwaky` and `.venv` in `.git/info/exclude` with a local ignore file as fallback.

#### Edge Cases

- Target directory absent, symlinks already present, workspace outside a repository, no isolated virtualenv.

#### Technical Specification

| Aspect | Detail |
|--------|--------|
| **Input** | `target_dir`, defaulting to the current directory |
| **Output** | A JSON string detailing created XDG paths, symlinks, and exclusion status |
| **Protocol** | stdio |
| **Method** | `vision_init` |
| **Event** | None |
| **Error** | Filesystem failures return a JSON error object naming the path that failed |

#### Test

| Context | When Action | Then Observable Result |
|---------|-------------|------------------------|
| empty directory | call vision_init | reports created XDG paths, symlinks, and exclusion status |

#### Metric

| Target Metric | Value |
|---------------|-------|
| Provisioning completeness | all reported artifacts present in summary |

### FR-MCP-003: Discover commands

**Description:** Return the available workspace, image, and video command catalog for agent planning.

#### Business Logic

- The catalog contains every public command and never advertises removed or internal commands.

#### Edge Cases

- Unknown domain, empty domain, command additions.

#### Technical Specification

| Aspect | Detail |
|--------|--------|
| **Input** | Optional `domain` filter taking `workspace`, `image`, or `video` |
| **Output** | JSON array for a filtered domain or a JSON object containing all domains |
| **Protocol** | stdio |
| **Method** | `vision_list_commands` |
| **Event** | None |
| **Error** | An unknown domain returns the full supported catalog rather than a misleading partial result |

#### Test

| Context | When Action | Then Observable Result |
|---------|-------------|------------------------|
| unknown domain | call vision_list_commands | returns the full supported catalog |

#### Metric

| Target Metric | Value |
|---------------|-------|
| Catalog accuracy | zero removed or internal commands advertised |

### FR-MCP-004: Read help documentation

**Description:** Return workspace usage documentation, or one selected section of it.

#### Business Logic

- Help content is read from the repository's `SKILL.md` file when present, falling back to a concise built-in summary.

#### Edge Cases

- Missing guide file, unknown section, stale section heading.

#### Technical Specification

| Aspect | Detail |
|--------|--------|
| **Input** | `section` taking `all`, `workspace`, `image`, or `video` |
| **Output** | Markdown text |
| **Protocol** | stdio |
| **Method** | `vision_help` |
| **Event** | None |
| **Error** | A clear not-found message is returned together with the list of supported sections |

#### Test

| Context | When Action | Then Observable Result |
|---------|-------------|------------------------|
| unknown section | call vision_help | returns a not-found message listing supported sections |

#### Metric

| Target Metric | Value |
|---------------|-------|
| Help availability | 100% of requests return Markdown content |

### FR-MCP-005: Report status

**Description:** Report configuration, package, and system dependency readiness through shared utilities.

#### Business Logic

- Reports reachability of the external endpoint through the shared connectivity checker.
- Reports the detected configuration source through the shared configuration handler.
- Reports system binary presence through the shared dependency checker.

#### Edge Cases

- Unreachable local endpoint, non-standard configuration locations, missing system binaries.

#### Technical Specification

| Aspect | Detail |
|--------|--------|
| **Input** | None |
| **Output** | JSON or structured status text |
| **Protocol** | stdio |
| **Method** | `vision_status` |
| **Event** | None |
| **Error** | A structured degraded-state payload is returned instead of an uncaught exception |

#### Test

| Context | When Action | Then Observable Result |
|---------|-------------|------------------------|
| unreachable endpoint | call vision_status | returns a degraded payload instead of raising |

#### Metric

| Target Metric | Value |
|---------------|-------|
| Readiness report latency | under 500 ms |
| Error containment | zero uncaught exceptions reaching the client |

### FR-MCP-006: Cancel running operations

**Description:** Report active operations and allow cancellation when background jobs are registered.

#### Business Logic

- Synchronous handlers return a clean response indicating zero cancellable background tasks.

#### Edge Cases

- Non-existent job identifier, no registered background jobs.

#### Technical Specification

| Aspect | Detail |
|--------|--------|
| **Input** | Optional `job_id` |
| **Output** | JSON response containing the active job count or a cancellation confirmation |
| **Protocol** | stdio |
| **Method** | `vision_cancel` |
| **Event** | None |
| **Error** | Structured JSON describes unsupported or missing jobs |

#### Test

| Context | When Action | Then Observable Result |
|---------|-------------|------------------------|
| no registered jobs | call vision_cancel | reports zero cancellable tasks |
| unknown identifier | call vision_cancel | describes the missing job |

#### Metric

| Target Metric | Value |
|---------------|-------|
| Cancellation response shape | always JSON |

## Public Interface

| Agent | Aggregate | Method | Request | Response |
|-------|-----------|--------|---------|----------|
| MCP client | MCP Tool Surface | `vision_execute` | command name and command options | JSON result or JSON error object |
| MCP client | MCP Tool Surface | `vision_init` | `target_dir` | JSON provisioning summary |
| MCP client | MCP Tool Surface | `vision_list_commands` | optional `domain` | JSON array or object of commands |
| MCP client | MCP Tool Surface | `vision_help` | `section` | Markdown text |
| MCP client | MCP Tool Surface | `vision_status` | none | JSON or structured readiness text |
| MCP client | MCP Tool Surface | `vision_cancel` | optional `job_id` | JSON job count or cancellation confirmation |
| MCP Tool Surface | Root Dispatcher | `execute_in_process` | command name and keyword arguments | command output |

## Reference

| Document | Link |
|----------|------|
| PRD | [PRD.md](../../PRD.md) |
| Backlog | [BACKLOG.md](BACKLOG.md) |
| Roadmap | [ROADMAP.md](../../ROADMAP.md) |
| Architecture | [ARCHITECTURE.md](../../ARCHITECTURE.md) |