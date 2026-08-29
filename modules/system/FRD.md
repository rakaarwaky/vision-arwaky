# FRD — System & Workspace Management

## System Overview

The `system` module manages core infrastructure and application-level lifecycle services for Vision Arwaky across 3 primary areas:
1. **Workspace Initialization & XDG Management**: Provisioning local workspaces, XDG Base Directory specification compliance (`~/.config/vision-arwaky`, `~/.local/share/vision-arwaky`, `~/.cache/vision-arwaky`, `~/.local/state/vision-arwaky`), embedding `.agents/skills/vision-arwaky/SKILL.md`, and managing `.git/info/exclude`.
2. **Configuration Management**: Reading and resolving settings across XDG/env/local files, and overwriting/mutating persistent configuration values.
3. **Job Management & Process Lifecycle**: Monitoring server and dependency status, tracking active jobs, and handling process cancellation/cleanup.

```text
CLI / MCP Surface
       │
       ▼
RootDispatcher
       │
       ▼
SystemOrchestrator
       │
       ├── CapabilitiesSystemWorkspace (XDG + Skill + Symlinks + Git Exclude)
       ├── CapabilitiesSystemConfiguration (Read / Overwrite config YAML)
       └── CapabilitiesSystemJob (Process tracking / Cancellation / Status)
```

## Functional Requirements

### FR-SYS-001: Workspace Initialization & XDG Management
- **Description:** Initialize and provision a target workspace according to the Linux XDG Base Directory Specification.
- **Input:** Target workspace directory (default: `.`).
- **Behavior:**
  1. **XDG Standard Layout**: Ensure `$XDG_CONFIG_HOME/vision-arwaky`, `$XDG_DATA_HOME/vision-arwaky`, `$XDG_CACHE_HOME/vision-arwaky`, and `$XDG_STATE_HOME/vision-arwaky` exist.
  2. **Skill Embedding**: Write embedded `SKILL.md` to `.agents/skills/vision-arwaky/SKILL.md` in the target workspace.
  3. **Workspace Symlinks**: Create `.vision-arwaky/` directory containing direct symlinks to XDG targets (`log` -> state, `data` -> data, `cache` -> cache).
  4. **Isolated Virtualenv Link**: If an isolated XDG virtualenv exists (`~/.local/share/vision-arwaky/venv`), symlink `.venv` in the target workspace.
  5. **Git Exclusion**: Ensure `.vision-arwaky` and `.venv` are ignored via local `.git/info/exclude` (if inside a git repository) or fallback `.gitignore`.
- **Output:** Structured JSON summary of created paths, symlinks, and exclusion status.

### FR-SYS-002: Configuration Management (Read & Overwrite Config)
- **Description:** Manage persistent and runtime configuration values with user-first XDG precedence.
- **Capabilities:**
  1. **Read Config (Baca Config)**:
     - Precedence: Environment variables (`LLAMA_API_URL`, `LLAMA_API_KEY`, `LLAMA_MODEL`) > User XDG file (`~/.config/vision-arwaky/config.yaml`) > Repository local (`./config.yaml`).
     - Return resolved configuration dictionary or query specific keys (e.g. `backend`, `external.url`, `external.model`).
  2. **Overwrite Config (Timpa Config Value)**:
     - Mutate key-value pairs in the persistent user configuration file (`~/.config/vision-arwaky/config.yaml`).
     - Support updating scalar and nested fields (e.g., changing backend endpoint, default model, or API keys).
     - Deep merge with existing values without losing unmentioned configuration keys.
- **Output:** Read configuration payload or confirmation of overwritten key and updated file path.

### FR-SYS-003: Job Management & Process Lifecycle
- **Description:** Manage in-flight vision processes, server status monitoring, and operation cancellation.
- **Capabilities:**
  1. **Server Status Monitoring**: Inspect external LLM endpoint connectivity, system binary availability (`ffmpeg`, `tesseract`), and Python library readiness (`cv2`, `PIL`, `pytesseract`).
  2. **Active Job Tracking**: Maintain registry of running asynchronous video/image operations.
  3. **Job Cancellation**: Gracefully terminate and clean up running processes by `job_id`.
- **Output:** JSON server status report or job cancellation confirmation.
