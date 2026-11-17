# FRD — Shared Foundation

## Feature Overview

The shared module is the foundation layer for Vision Arwaky. In compliance with the Agentic Engineering System (AES) it carries the Taxonomy, Contract, and Utility layers only, and never carries capabilities, agents, surfaces, or composition concerns. It provides taxonomy (VOs, errors, events, constants), contract (protocols and aggregates), and utility (stateless functions). Every layer above depends on it, and it depends on nothing above itself.

## Functional Requirements

### FR-SHR-001: Provide the taxonomy layer

**Description:** Provide immutable, domain-stable value objects, errors, events, and constants. Domain concepts defined by feature specifications become reusable taxonomy types: command-domain classification (`IMAGE`, `VIDEO`, `SYSTEM` with their command sets), vision value objects (`AnalysisPrompt`, `BoundingBox`, `CommandName`, `CommandOutput`, `FilePath`, `IntervalSeconds`, `VideoInfo`, `VisionAnalysis`, `VideoUnderstanding`), XDG directory paths (`config_dir`, `data_dir`, `cache_dir`, `state_dir`, `bin_dir`), tunable constants (`DEFAULT_VLM_TIMEOUT_S`, `SCENE_THRESHOLD`, `MIN_MOTION_AREA`, `EMBEDDED_SKILL_MD`), the domain error hierarchy (`VisionDomainError`, `ImageProcessingError`, `VideoProcessingError`, `InvalidParameterError`), and domain events (`SceneChange`, `MotionEvent`).

#### Business Logic

- Zero dependencies on upper layers; primitive types appear only in value objects and constants.
- Errors and events are built from taxonomy types only.
- Domain errors carry enough context for the caller to classify the failure without reading the source.

#### Edge Cases

- A feature introduces a concept that already exists: extend the existing type rather than add a twin.
- A constant is tuned per deployment: the value stays a taxonomy constant, never an inline literal.

#### Technical Specification

| Aspect | Detail |
|--------|--------|
| **Input** | Domain concepts defined by feature specifications (shape: taxonomy concepts), sourced from feature specifications. |
| **Output** | Reusable taxonomy types — value objects, constants, error hierarchy, events, and XDG paths — exposed to every upper layer. |
| **Protocol** | None (taxonomy layer defines types; no protocol ports). |
| **Method** | None (types only, no capability method). |
| **Event** | `SceneChange`, `MotionEvent` (domain events defined by the taxonomy). |
| **Error** | `VisionDomainError`, `ImageProcessingError`, `VideoProcessingError`, `InvalidParameterError` — the caller sees a domain error carrying classification context. |

#### Test

| Context | When Action | Then Observable Result |
|---------|-------------|------------------------|
| Taxonomy value object | Constructing a value object twice from equal input | Yields two instances that cannot be mutated afterwards (immutability). |
| Taxonomy type reuse | A feature introduces a concept that already exists | The existing type is extended rather than a twin added. |
| Primitive containment | A type audit runs over taxonomy declarations | Primitive types appear only in value objects and constants, never in entity, error, or event fields. |

#### Metric

| Target Metric | Value |
|---------------|-------|
| Primitive leakage in entity/error/event fields | zero (type audit of taxonomy declarations) |
| Upper-layer imports | zero imports from capability, agent, surface, or composition layers (import audit) |
| Value object immutability | every value object frozen after construction (construction-then-mutation test) |

### FR-SHR-002: Provide the contract layer

**Description:** Provide pure abstract definitions for protocol ports and the aggregate facade. Capability seams contributed by the feature modules become protocol ports `ImageProcessingProtocol`, `TesseractOCRProtocol`, `LLMVisionProtocol`, `VideoProcessingProtocol`, `VideoAnalysisProtocol`, `ObjectTrackingProtocol`, `VideoUnderstandingProtocol`, `FFmpegVideoProtocol`, `WorkspaceProtocol`, `SystemConfigurationProtocol`, `SystemJobProtocol`, plus the aggregate facade `RegistryServiceAggregate`.

#### Business Logic

- Declarations only, without method bodies or business logic.
- Every method signature uses taxonomy value objects rather than primitives.
- Aggregates are composite entry points and are excluded from the capability-seam count.

#### Edge Cases

- A seam grows a second unrelated responsibility: split it into another protocol rather than widen one port.
- A method needs a primitive: wrap it in a value object.

#### Technical Specification

| Aspect | Detail |
|--------|--------|
| **Input** | Capability seams contributed by the feature modules (shape: protocol ports and the aggregate facade). |
| **Output** | Protocol ports (`ImageProcessingProtocol`, `TesseractOCRProtocol`, `LLMVisionProtocol`, `VideoProcessingProtocol`, `VideoAnalysisProtocol`, `ObjectTrackingProtocol`, `VideoUnderstandingProtocol`, `FFmpegVideoProtocol`, `WorkspaceProtocol`, `SystemConfigurationProtocol`, `SystemJobProtocol`) plus the aggregate facade `RegistryServiceAggregate`. |
| **Protocol** | `RegistryServiceAggregate` (aggregate facade) and the eleven protocol ports; the capability implements the port and the agent calls it. |
| **Method** | Capability methods declared on the ports; aggregate method `execute_in_process` as the single composite entry point. |
| **Event** | None. |
| **Error** | Contract declarations raise no behaviour of their own; the caller sees failure semantics stated by the taxonomy errors the signatures carry. |

#### Test

| Context | When Action | Then Observable Result |
|---------|-------------|------------------------|
| Protocol port | A protocol port with a primitive argument is type-audited | Rejected and replaced by a value object. |
| Contract declarations | A contract-purity review runs | Zero method bodies in protocol and aggregate declarations. |
| Aggregate facade | A surface calls `execute_in_process` | A single composite entry point runs a domain command and returns the command output. |

#### Metric

| Target Metric | Value |
|---------------|-------|
| Contract purity | zero method bodies in protocol and aggregate declarations (declaration review) |
| Primitive leakage in signatures | zero primitives in port signatures (type audit of taxonomy declarations) |

### FR-SHR-003: Provide the utility layer

**Description:** Provide reusable, stateless, domain-agnostic functions. Values, paths, and options supplied by callers in any layer become configuration load, merge, and serialize helpers; package and system binary availability checks; an endpoint connectivity check; package version resolution; video frame extraction helpers; command output serialization helpers; pure image operations (grayscale, threshold, blur, edge, contour, histogram, optical flow); a synchronous bridge for coroutines; path normalization and executable validation.

#### Business Logic

- Stateless functions only — no classes, no instance state, no global mutable singletons.
- Utilities depend on taxonomy and never on contracts, capabilities, agents, surfaces, or composition.

#### Edge Cases

- Missing package or binary.
- Unreadable configuration file.
- Coroutine that completes with an error.
- Path with a trailing separator or symlinked segment.

#### Technical Specification

| Aspect | Detail |
|--------|--------|
| **Input** | Values, paths, and options supplied by callers in any layer (shape: function arguments). |
| **Output** | Helper return values and pure image-op results returned to the caller; no persisted state. |
| **Protocol** | None (utility layer is stateless functions, not protocol ports). |
| **Method** | Stateless utility functions: configuration helpers, availability checks, image operations, and the coroutine bridge. |
| **Event** | None. |
| **Error** | Availability checks report absence as a value rather than an exception; parsing helpers surface a typed taxonomy error naming the input that failed — the caller sees a value or a typed taxonomy error. |

#### Test

| Context | When Action | Then Observable Result |
|---------|-------------|------------------------|
| Stateless utility | A utility called twice with equal input | Returns equal output and shares no state between calls. |
| Availability check | An availability check on a missing binary | Reports absence as a value and raises no exception. |
| Upper-layer import | A utility that imports from a capability, agent, surface, or composition layer | Fails the import audit. |

#### Metric

| Target Metric | Value |
|---------------|-------|
| Utility statefulness | zero in-memory mutable state (review of utility boundaries plus a state-reuse test) |

## Public Interface

| Agent | Aggregate | Method | Request | Response |
|-------|-----------|--------|---------|----------|
| Surface / Agent | `RegistryServiceAggregate` | `execute_in_process` | Command name and keyword arguments | Command output (`CommandOutput`), or a taxonomy error |
| Capabilities layer | Protocol ports (e.g. `ImageProcessingProtocol`) | `analyze_screenshot`, `extract_text`, `compare_screenshots` | Image path, prompt, language code | Analysis result, OCR text, comparison report, or a taxonomy error |
| Capabilities layer | `VideoProcessingProtocol` | `get_info`, `check_corruption`, `extract_frames` | Video path, sampling parameters | Video metadata, decodability flag, frame paths, or a taxonomy error |
| Capabilities layer | `VideoAnalysisProtocol` | `detect_scenes`, `detect_motion` | Video path, threshold | Scene boundary list, motion events, or a taxonomy error |
| Capabilities layer | `ObjectTrackingProtocol` | `track_object` | Video path, bounding box, frame budget | Trajectory points, or a taxonomy error |
| Capabilities layer | `VideoUnderstandingProtocol` | `analyze` | Video path, prompt | Understanding result, or a taxonomy error |
| Capabilities layer | `FFmpegVideoProtocol` | `run` | Argument list, output flag, timeout | Command output, or a taxonomy error |
| Capabilities layer | `WorkspaceProtocol` | `init_workspace` | Target workspace directory | Provisioning summary, or a taxonomy error |
| Capabilities layer | `SystemConfigurationProtocol` | `get_config`, `set_config` | Configuration key and value | Resolved value, overwrite confirmation, or a taxonomy error |
| Capabilities layer | `SystemJobProtocol` | `get_status`, `cancel_job` | Job identifier | Readiness report, cancellation confirmation, or a taxonomy error |

## Reference

| Artifact | Purpose | Link |
|----------|---------|------|
| PRD | Business goals, user stories, and scope | [PRD.md](../../PRD.md) |
| Backlog | Task tracking, epics, and implementation status | [BACKLOG.md](BACKLOG.md) |
| Roadmap | Timeline, phasing, and dependencies | [ROADMAP.md](../../ROADMAP.md) |
| Architecture | System boundaries, tech stack, and infrastructure | [ARCHITECTURE.md](../../ARCHITECTURE.md) |
