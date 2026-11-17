# FRD — System Container

## Feature Overview

The system module manages workspace provisioning, XDG layout, configuration, and job lifecycle for Vision Arwaky. It sits below the CLI and MCP surfaces, above the shared foundation, and is reached only through the root dispatcher. It owns workspace initialization under the Linux XDG Base Directory Specification, configuration read/write with user-first XDG precedence, and in-flight process tracking with readiness monitoring and cancellation.

## Functional Requirements

### FR-SYS-001: Provision workspace and XDG layout

**Description:** Initialize and provision a target workspace according to the Linux XDG Base Directory Specification.

#### Business Logic

- Create `$XDG_CONFIG_HOME/vision-arwaky`, `$XDG_DATA_HOME/vision-arwaky`, `$XDG_CACHE_HOME/vision-arwaky`, and `$XDG_STATE_HOME/vision-arwaky`.
- Write the embedded skill guide to `.agents/skills/vision-arwaky/SKILL.md`.
- Create `.vision-arwaky/` holding symlinks `log` to state, `data` to data, and `cache` to cache.
- When an isolated XDG virtualenv exists, symlink `.venv` in the target workspace.
- Add `.vision-arwaky` and `.venv` to `.git/info/exclude` inside a repository, otherwise to a local `.gitignore`.

#### Edge Cases

- Target directory does not exist yet.
- Valid symlinks already present.
- Broken or mismatched symlinks.
- Workspace not inside a repository.
- No isolated virtualenv present.

#### Technical Specification

| Aspect | Detail |
|--------|--------|
| **Input** | Target workspace directory path; defaults to the current directory. Source: caller command request. |
| **Output** | Structured summary of created directories, symlinks, and exclusion entries. Destination: caller. |
| **Protocol** | `IWorkspaceProtocol` |
| **Method** | `init_workspace` |
| **Event** | None |
| **Error** | Permission denial, read-only targets, and unresolvable XDG variables abort provisioning and return a structured error naming the path that failed. |

#### Test

| Context | When Action | Then Observable Result |
|---------|-------------|------------------------|
| Empty workspace directory | `init_workspace` is invoked | Four XDG directories, skill guide, workspace symlinks, and exclusion entries are created; summary names every created path |
| Same workspace provisioned twice | `init_workspace` is invoked | Valid symlinks remain in place and the same summary is reported |

#### Metric

| Target Metric | Value |
|---------------|-------|
| Workspace Provisioning Latency | Under 2 s for an empty workspace |

### FR-SYS-002: Read and overwrite configuration

**Description:** Manage persistent and runtime configuration values with user-first XDG precedence.

#### Business Logic

- Read precedence is environment variables (`LLAMA_API_URL`, `LLAMA_API_KEY`, `LLAMA_MODEL`) over the user XDG file `~/.config/vision-arwaky/config.yaml` over the repository local `./config.yaml`.
- Writes mutate the user XDG file only.
- Scalar and nested fields are both writable.
- A write deep-merges into existing values so unmentioned keys survive.

#### Edge Cases

- One precedence level missing or empty.
- Unknown key requested.
- Nested key whose intermediate maps are absent.
- Key written while a read is in flight.

#### Technical Specification

| Aspect | Detail |
|--------|--------|
| **Input** | Optional configuration key for reads; key and value pairs for writes. Source: caller command request. |
| **Output** | Resolved configuration payload for the whole document or a single key, or a confirmation naming the overwritten key and the updated file. Destination: caller. |
| **Protocol** | `ISystemConfigurationProtocol` |
| **Method** | `get_config`, `set_config` |
| **Event** | None |
| **Error** | Unparseable configuration content, unwritable target path, and invalid key types return a structured error naming the file and the key, and leave the previous configuration content intact. |

#### Test

| Context | When Action | Then Observable Result |
|---------|-------------|------------------------|
| Configuration key read with environment variable set | `get_config` is invoked | The environment value is returned ahead of both files |
| Nested key overwritten | `set_config` is invoked | Every unmentioned key in the persistent user configuration survives |

#### Metric

| Target Metric | Value |
|---------------|-------|
| Configuration Read Overhead | Under 50 ms per resolution |

### FR-SYS-003: Manage jobs and process lifecycle

**Description:** Manage in-flight vision processes, readiness monitoring, and operation cancellation.

#### Business Logic

- Readiness reports external LLM endpoint connectivity, availability of system binaries `ffmpeg` and `tesseract`, and availability of packages `cv2`, `PIL`, and `pytesseract`.
- The registry tracks every running asynchronous video or image operation.
- Cancellation targets one job by identifier and releases its resources.

#### Edge Cases

- Endpoint unreachable.
- A binary or package absent.
- Unknown job identifier.
- No registered jobs.
- A process that ignores the first termination request.

#### Technical Specification

| Aspect | Detail |
|--------|--------|
| **Input** | Optional job identifier for cancellation; no input for readiness queries. Source: caller command request. |
| **Output** | Structured readiness report covering endpoint connectivity, binary and package availability, and the active job registry, or a cancellation confirmation. Destination: caller. |
| **Protocol** | `ISystemJobProtocol` |
| **Method** | `get_status`, `cancel_job` |
| **Event** | None |
| **Error** | Missing dependencies are reported as a degraded payload instead of an exception; an unknown identifier returns a structured "no such job" response; a stubborn process is escalated and the outcome reported. |

#### Test

| Context | When Action | Then Observable Result |
|---------|-------------|------------------------|
| Readiness query with unreachable endpoint | `get_status` is invoked | A degraded payload is returned that still lists binary and package availability |
| Cancellation of unknown job | `cancel_job` is invoked | A structured response naming the missing identifier is returned instead of raising |

#### Metric

| Target Metric | Value |
|---------------|-------|
| Readiness Report Latency | Under 500 ms |
| Cancellation Response | Under 3 s to release a registered job |

## Public Interface

| Aspect | Detail |
|--------|--------|
| Agent | `SystemOrchestrator` |
| Aggregate | `IRegistryServiceAggregate` |
| Method | `execute_in_process` |
| Request | System command parameters (`init_workspace`, `get_config`, `set_config`, `get_status`, `cancel_job`) |
| Response | `CommandOutput` |

## Reference

| Artifact | Purpose | Link |
|----------|---------|------|
| PRD | Business goals, user stories, and scope | [PRD.md](../../PRD.md) |
| Backlog | Task tracking, epics, and implementation status | [BACKLOG.md](BACKLOG.md) |
| Roadmap | Timeline, phasing, and dependencies | [ROADMAP.md](../../ROADMAP.md) |
| Architecture | System boundaries, tech stack, and infrastructure | [ARCHITECTURE.md](../../ARCHITECTURE.md) |
