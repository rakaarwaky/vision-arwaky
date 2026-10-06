# FRD — System & Workspace Management

## Reference

- Product requirements: [PRD.md](../../PRD.md)
- Feature backlog: [BACKLOG.md](BACKLOG.md)

## System Overview

The system module owns core infrastructure and application lifecycle services for Vision Arwaky across three areas: workspace initialization and XDG directory management, configuration reading and overwriting, and job tracking with process cancellation. It sits below the CLI and MCP surfaces, above the shared foundation, and is reached only through the root dispatcher.

```text
CLI / MCP surface
       │
       ▼
Root entry dispatcher
       │
       ▼
System orchestrator
       ├── Workspace capability (XDG layout, skill guide, exclusions)
       ├── Configuration capability (read / overwrite config)
       └── Job capability (status, tracking, cancellation)
```

## Functional Requirements

### FR-SYS-001: Provision workspace and XDG layout

- **Description**: Initialize and provision a target workspace according to the Linux XDG Base Directory Specification.
- **Input**: Target workspace directory path; defaults to the current directory.
- **Output**: Structured summary of created directories, symlinks, and exclusion entries.
- **Business Rules**: Create `$XDG_CONFIG_HOME/vision-arwaky`, `$XDG_DATA_HOME/vision-arwaky`, `$XDG_CACHE_HOME/vision-arwaky`, and `$XDG_STATE_HOME/vision-arwaky`; write the embedded skill guide to `.agents/skills/vision-arwaky/SKILL.md`; create `.vision-arwaky/` holding symlinks `log` to state, `data` to data, and `cache` to cache; when an isolated XDG virtualenv exists, symlink `.venv` in the target workspace; add `.vision-arwaky` and `.venv` to `.git/info/exclude` inside a repository, otherwise to a local `.gitignore`.
- **Edge Cases**: Target directory does not exist yet; valid symlinks already present; broken or mismatched symlinks; workspace not inside a repository; no isolated virtualenv present.
- **Error Handling**: Permission denial, read-only targets, and unresolvable XDG variables abort provisioning and return a structured error naming the path that failed.

### FR-SYS-002: Read and overwrite configuration

- **Description**: Manage persistent and runtime configuration values with user-first XDG precedence.
- **Input**: Optional configuration key for reads; key and value pairs for writes.
- **Output**: Resolved configuration payload for the whole document or a single key, or a confirmation naming the overwritten key and the updated file.
- **Business Rules**: Read precedence is environment variables (`LLAMA_API_URL`, `LLAMA_API_KEY`, `LLAMA_MODEL`) over the user XDG file `~/.config/vision-arwaky/config.yaml` over the repository local `./config.yaml`; writes mutate the user XDG file only; scalar and nested fields are both writable; a write deep-merges into existing values so unmentioned keys survive.
- **Edge Cases**: One precedence level missing or empty; unknown key requested; nested key whose intermediate maps are absent; key written while a read is in flight.
- **Error Handling**: Unparseable configuration content, unwritable target path, and invalid key types return a structured error naming the file and the key, and leave the previous configuration content intact.

### FR-SYS-003: Manage jobs and process lifecycle

- **Description**: Manage in-flight vision processes, readiness monitoring, and operation cancellation.
- **Input**: Optional job identifier for cancellation; no input for readiness queries.
- **Output**: Structured readiness report covering endpoint connectivity, binary and package availability, and the active job registry, or a cancellation confirmation.
- **Business Rules**: Readiness reports external LLM endpoint connectivity, availability of system binaries `ffmpeg` and `tesseract`, and availability of packages `cv2`, `PIL`, and `pytesseract`; the registry tracks every running asynchronous video or image operation; cancellation targets one job by identifier and releases its resources.
- **Edge Cases**: Endpoint unreachable; a binary or package absent; unknown job identifier; no registered jobs; a process that ignores the first termination request.
- **Error Handling**: Missing dependencies are reported as a degraded payload instead of an exception; an unknown identifier returns a structured "no such job" response; a stubborn process is escalated and the outcome reported.

## API Contract

### Protocol API

| Method | Input | Output | Error | Event | Description |
|--------|-------|--------|-------|-------|-------------|
| `init_workspace` | target workspace directory | provisioning summary | workspace provisioning error | none | Provision the XDG layout, skill guide, workspace symlinks, and exclusion entries |
| `get_config` | optional configuration key | resolved value or full payload | configuration read error | none | Resolve configuration across environment, user file, and repository file precedence |
| `set_config` | configuration key and new value | overwrite confirmation with the updated file | configuration write error | none | Deep-merge one key into the persistent user configuration |
| `get_status` | none | structured readiness report | readiness report error | none | Report endpoint connectivity, binary and package availability, and active jobs |
| `cancel_job` | job identifier | cancellation confirmation | cancellation error | none | Terminate and clean up one registered asynchronous operation |

### Aggregate API

| Method | Input | Output | Error | Event | Description |
|--------|-------|--------|-------|-------|-------------|
| `execute_in_process` | command name and keyword arguments | command output | command execution error | none | Single composite entry point the CLI and MCP surfaces call to run a domain command |

## Integration Points

| System | Direction | Purpose | Failure mode |
|--------|-----------|---------|--------------|
| External LLM endpoint | out | Report connectivity for configuration and readiness checks | unreachable -> degraded readiness payload |
| System binaries and packages | out | Prove that media and OCR tooling is available | missing -> listed as unavailable, command refused |
| Host filesystem | out | Create XDG directories, workspace symlinks, and exclusion entries | permission denied -> structured error naming the path |
| Git metadata | out | Exclude workspace artifacts from version control | no repository -> fall back to a local ignore file |
| CLI and MCP surfaces | in | Invoke workspace, configuration, readiness, and cancellation operations | invalid input -> structured error response |

## Non-functional Requirements

| Metric | Target | Measurement method |
|--------|--------|--------------------|
| Workspace provisioning latency | under 2 s for an empty workspace | timed provisioning run over a fresh directory |
| Readiness report latency | under 500 ms | timed readiness query with dependencies running |
| Configuration read overhead | under 50 ms per resolution | timed read across all three precedence levels |
| Cancellation response | under 3 s to release a registered job | timed cancellation of a running operation |
| Configuration write atomicity | no partial configuration content after a failed write | fault-injected write followed by content inspection |

## Test Scenarios

- Provisioning an empty directory creates the four XDG directories, the skill guide, the workspace symlinks, and the exclusion entries, and the summary names every created path.
- Provisioning the same workspace twice leaves valid symlinks in place and reports the same summary.
- Reading a configuration key with the environment variable set returns the environment value ahead of both files.
- Overwriting a nested key keeps every unmentioned key in the persistent user configuration.
- Cancelling an unknown job returns a structured response naming the missing identifier instead of raising.
- A readiness query with an unreachable endpoint returns a degraded payload that still lists binary and package availability.

## Assumptions & Constraints

- XDG base directories follow the Linux XDG Base Directory Specification, and unset variables resolve to the documented defaults.
- The user configuration file is the only file configuration writes touch; repository-local configuration stays read-only.
- Cancellation applies to processes registered through the job registry; processes started outside it are out of scope.
- Tuning constants such as frame interval, scene threshold, and motion area are not configuration keys in this module.

## Glossary

- **XDG Base Directory Specification**: Linux convention fixing where user configuration, data, cache, and state files live.
- **Workspace**: The project directory the provisioning step prepares for agent use.
- **Provisioning**: Creating the directory layout, symlinks, skill guide, and exclusion entries a workspace needs.
- **Readiness report**: Structured answer naming endpoint connectivity, binary availability, and package availability.
- **Job registry**: The list of running asynchronous operations tracked for status and cancellation.
