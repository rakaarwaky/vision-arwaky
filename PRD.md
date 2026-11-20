# PRD — Vision Arwaky

## Project Overview

Vision Arwaky is a Python computer-vision toolkit for AI agents and technical users who need local, scriptable access to image and video intelligence. The CLI and MCP server expose a single, documented command surface for workspace initialization, image analysis, and bounded smart-video understanding. Deterministic media operations stay local; vision-language analysis is an optional OpenAI-compatible adapter.

```text
caller (CLI | MCP | TUI)
        │
        ▼
domain container (image | video | system)
        │
        ▼
orchestrator → capability → contract → taxonomy / utility
```

- Primary business goal: give agent integrators and developers one local package that covers image and video intelligence without per-feature scripts.
- Primary user goal: send a supported command through the CLI or MCP interface, get structured JSON, and understand failures without knowing the internal adapter graph.
- Strategic objective: keep deterministic media operations offline and reproducible while vision-language analysis remains an optional, swappable enhancement.

## Goals

- Provide a stable image and video command surface (init, image, video).
- Support agent integration through six stable MCP tools.
- Keep deterministic processing local and reproducible.
- Keep architecture maintainable with zero AES violations.

## Non-Goals

- A bundled vision-language model or model weights; the external backend is configured separately.
- A hosted SaaS control plane, user accounts, or cloud media storage.
- Visual-memory storage and search, model training, or deep-learning object detection.

## Target Users

| Persona | Need | Current Pain | Desired Outcome |
|---------|------|--------------|-----------------|
| AI agent developer | Discoverable commands, stable JSON, status reporting | Capability split across unrelated scripts | One MCP server exposing six stable tools |
| Computer-vision developer | Local CLI for image and video intelligence | Ad-hoc tools with inconsistent output | Documented commands with structured output |
| QA and automation engineer | Deterministic commands and CI-runnable fixtures | Flaky manual media checks | Reproducible test suite without a live VLM |
| Technical maintainer | Explicit layer boundaries and DI wiring | Drifted architecture across modules | AES layer contract enforced by CI gates |

## Scope

### In Scope

- Workspace initialization, XDG directory layout, configuration, and job lifecycle.
- Image analysis with deterministic fallback via VLM.
- Bounded smart-video understanding with key-frame sampling, per-frame VLM analysis, and summary generation.
- MCP tools for init, execute, discovery, help, status, and cancellation.
- Local operation with FFmpeg and OpenCV; CI quality gates across Python 3.12 and 3.13.

### Out of Scope

- Visual-memory storage or search commands.
- A hosted SaaS control plane, user accounts, or cloud media storage.
- Model training, deep-learning object detection, or a bundled vision-language model.

---

## Project Requirements

### PR-VA-001: CLI and TUI command surface

<!-- Tier P0: entry -001 is always P0. -->

#### User Stories

| As a | I want | So that | Priority |
|------|--------|---------|----------|
| Developer | to run every command through one console script | installation is simple | P0 |
| Operator | to browse configuration and status in a TUI | interactive workflows stay fast | P0 |
| CLI user | to initialize a workspace with XDG layout | the runtime artifacts land in the right directories | P0 |

#### Proposed Solution

The CLI parser and command handlers live in the `cli` feature; the TUI is a surface over the same domain containers. Both delegate through the root orchestrator resolver so command behavior stays identical across surfaces. The CLI dispatches three public commands: `init`, `image`, and `video`.

#### Main User Flow

1. The user runs a console script (`va`, `vision-arwaky-cli`, or `vision-arwaky-tui`).
2. The CLI controller parses argv into a command namespace.
3. The command handler resolves the domain container and invokes the orchestrator.
4. The result is rendered as JSON for the terminal or as rows for the TUI pane.

### PR-VA-002: Image intelligence command surface

<!-- Tier P1: the first P1 entry. -->

#### User Stories

| As a | I want | So that | Priority |
|------|--------|---------|----------|
| CLI user | to analyze an image with a VLM | images can be described without manual inspection | P1 |
| CLI user | to analyze a video frame or short clip through the image command | single-frame analysis is accessible | P1 |

#### Proposed Solution

The image feature owns analysis only. Each capability implements its protocol, and the image orchestrator composes them behind the aggregate the surfaces call.

#### Main User Flow

1. The caller sends `va image --image <path>` through the CLI or MCP.
2. The image orchestrator dispatches to the analysis capability.
3. The capability runs the vision adapter.
4. The result is wrapped in the command output envelope and returned as JSON.

### PR-VA-003: MCP agent integration surface

<!-- Tier P1: the first P1 entry. -->

#### User Stories

| As a | I want | So that | Priority |
|------|--------|---------|----------|
| AI agent | to discover commands through `vision_list_commands` | the agent can drive the CLI surface programmatically | P1 |
| AI agent | to read status and cancel running operations | failures and long runs are manageable | P1 |

#### Proposed Solution

The MCP server registers six stable tools over stdio: `vision_init`, `vision_execute`, `vision_list_commands`, `vision_help`, `vision_status`, and `vision_cancel`. Command discovery reflects the current CLI contract.

#### Main User Flow

1. The MCP server starts over stdio and registers the six tools.
2. The agent calls `vision_list_commands` to discover the command contract.
3. The agent calls `vision_execute` with a command name and arguments.
4. The server dispatches through the domain container and returns structured JSON.

### PR-VA-004: System workspace and provisioning surface

<!-- Tier P1: the first P1 entry. -->

#### User Stories

| As a | I want | So that | Priority |
|------|--------|---------|----------|
| CLI user | to initialize a workspace with XDG layout | the runtime artifacts land in the right directories | P1 |
| MCP agent | to execute a supported workspace command | the agent can provision and configure the workspace | P1 |
| Maintainer | to read and overwrite configuration | settings persist between runs | P1 |

#### Proposed Solution

The system feature owns workspace provisioning, XDG path resolution, configuration read/overwrite, and job lifecycle. The CLI and MCP surfaces dispatch workspace commands through the system orchestrator, which resolves ports injected by the root composition.

#### Main User Flow

1. Run `va init [target_dir]` or `vision_init` through MCP.
2. The orchestrator provisions `.vision-arwaky` symlinks and embeds the packaged skill guide.
3. Configuration is read from the user config directory with repository-local overrides.
4. Subsequent commands resolve their artifacts through the provisioned layout.

### PR-VA-005: Video intelligence command surface

<!-- Tier P1: the first P1 entry. -->

#### User Stories

| As a | I want | So that | Priority |
|------|--------|---------|----------|
| CLI user | to run bounded smart-video understanding | long videos get a capped, summarized analysis | P1 |
| Agent | to run bounded smart-video understanding | long videos get a capped, summarized analysis | P1 |

#### Proposed Solution

The video feature owns bounded smart understanding only. Frame sampling is capped, summary prompts are bounded, and temporary frames are removed after execution.

#### Main User Flow

1. The caller sends `va video --video <path>` through the CLI or MCP.
2. The video orchestrator resolves the understanding capability.
3. The capability decodes the video, samples frames uniformly, and runs VLM analysis.
4. Selected frames are analyzed by the VLM and synthesized into a bounded summary.

## Reference

| Artifact     | Purpose                                          | Link                        |
|--------------|--------------------------------------------------|-----------------------------|
| PRD          | Business goals and scope                         | [PRD.md](PRD.md)            |
| Backlog      | What is true now, with evidence                  | [BACKLOG.md](BACKLOG.md)    |
| Roadmap      | Timeline, phasing, and dependencies              | [ROADMAP.md](ROADMAP.md)    |
| Architecture | System boundaries, tech stack, and infrastructure | [ARCHITECTURE.md](ARCHITECTURE.md) |