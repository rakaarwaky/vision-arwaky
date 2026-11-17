# DATA — Shared Foundation (Taxonomy, Contract, Utility)

## Data Overview

The `shared` module is the kernel of the workspace. It holds the three foundation layers every feature depends on: taxonomy (value objects, errors, events, constants), contract (protocol ports and aggregate facades), and utility (stateless pure functions). It holds no business logic — only types, utilities, and interface definitions that other layers depend on.

## Data Requirements

### DT-SHARED-001: Command Domain Classification

| Type | Description |
|------|-------------|
| CommandDomain | Immutable classification of a command as `IMAGE`, `VIDEO`, or `SYSTEM`, each carrying its supported command set. Used by the CLI and MCP surfaces to route commands to the correct domain container. |

### DT-SHARED-002: Vision Value Objects

| Type | Description |
|------|-------------|
| VisionVOs | Immutable value objects shared across image and video features: `AnalysisPrompt`, `BoundingBox`, `CommandName`, `CommandOutput`, `FilePath`, `IntervalSeconds`, `VideoInfo`, `VisionAnalysis`, `VideoUnderstanding`. |

### DT-SHARED-003: XDG Directory Paths

| Type | Description |
|------|-------------|
| XDGPaths | Immutable value objects for XDG Base Directory paths: `config_dir`, `data_dir`, `cache_dir`, `state_dir`, `bin_dir`. Resolved once at startup and injected into the system container. |

### DT-SHARED-004: Tunable Constants

| Type | Description |
|------|-------------|
| VisionConstants | Compile-time constants for tunable parameters: `DEFAULT_VLM_TIMEOUT_S`, `SCENE_THRESHOLD`, `MIN_MOTION_AREA`, `MAX_TRACK_FRAMES`, `FRAME_EXTRACTION_INTERVAL_S`, `EMBEDDED_SKILL_MD`. |

### DT-SHARED-005: Domain Error Hierarchy

| Type | Description |
|------|-------------|
| DomainErrors | Domain-level error types: `VisionDomainError` (base), `ImageProcessingError`, `VideoProcessingError`, `InvalidParameterError`. Carry enough context for the caller to classify the failure. |

### DT-SHARED-006: Domain Events

| Type | Description |
|------|-------------|
| DomainEvents | Immutable domain event records: `SceneChange`, `MotionEvent`. Emitted by video analysis capabilities and consumed by downstream analysis. |

## Reference

| Artifact | Purpose | Link |
|----------|---------|------|
| PRD.md | Product requirements | [PRD.md](../../PRD.md) |
| BACKLOG.md | Backlog tracking | [BACKLOG.md](BACKLOG.md) |
| ROADMAP.md | Roadmap status | [ROADMAP.md](../../ROADMAP.md) |
| ARCHITECTURE.md | Layer contract | [ARCHITECTURE.md](../../ARCHITECTURE.md) |