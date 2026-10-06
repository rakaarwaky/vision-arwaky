# FRD — Shared Foundation (Taxonomy, Contract, Utility)

## Reference

- Product requirements: [PRD.md](../../PRD.md)
- Feature backlog: [BACKLOG.md](BACKLOG.md)

## System Overview

The shared module is the foundation layer for Vision Arwaky. In compliance with the Agentic Engineering System (AES) it carries the Taxonomy, Contract, and Utility layers only, and never carries capabilities, agents, surfaces, or composition concerns. Every layer above depends on it, and it depends on nothing above itself.

```text
       Surface Layer (CLI / MCP / TUI)
                     │
                     ▼
          Root Entry Points (Dispatcher)
          ┌──────────┼──────────┐
          ▼          ▼          ▼
        Image      Video      System
      (Agent)    (Agent)    (Agent)
          │          │          │
          └──────────┼──────────┘
                     │
                     ▼
      ┌─────────────────────────────┐
      │         Shared Module       │
      │ ┌─────────────────────────┐ │
      │ │ Contract Layer (ports)  │ │
      │ └─────────────────────────┘ │
      │ ┌─────────────────────────┐ │
      │ │ Utility Layer (pure fns)│ │
      │ └─────────────────────────┘ │
      │ ┌─────────────────────────┐ │
      │ │ Taxonomy Layer (VOs)    │ │
      │ └─────────────────────────┘ │
      └─────────────────────────────┘
```

## Functional Requirements

### FR-SHR-001: Provide the taxonomy layer

- **Description**: Provide immutable, domain-stable value objects, errors, events, and constants.
- **Input**: Domain concepts defined by feature specifications.
- **Output**: Reusable taxonomy types: command-domain classification (`IMAGE`, `VIDEO`, `SYSTEM` with their command sets), vision value objects (`AnalysisPrompt`, `BoundingBox`, `CommandName`, `CommandOutput`, `FilePath`, `IntervalSeconds`, `VideoInfo`, `VisionAnalysis`, `VideoUnderstanding`), XDG directory paths (`config_dir`, `data_dir`, `cache_dir`, `state_dir`, `bin_dir`), tunable constants (`DEFAULT_VLM_TIMEOUT_S`, `SCENE_THRESHOLD`, `MIN_MOTION_AREA`, `EMBEDDED_SKILL_MD`), the domain error hierarchy (`VisionDomainError`, `ImageProcessingError`, `VideoProcessingError`, `InvalidParameterError`), and domain events (`SceneChange`, `MotionEvent`).
- **Business Rules**: Zero dependencies on upper layers; primitive types appear only in value objects and constants; errors and events are built from taxonomy types only.
- **Edge Cases**: A feature introduces a concept that already exists (extend the existing type rather than add a twin); a constant is tuned per deployment (value stays a taxonomy constant, never an inline literal).
- **Error Handling**: Domain errors carry enough context for the caller to classify the failure without reading the source.

### FR-SHR-002: Provide the contract layer

- **Description**: Provide pure abstract definitions for protocol ports and the aggregate facade.
- **Input**: Capability seams contributed by the feature modules.
- **Output**: Protocol ports `ImageProcessingProtocol`, `TesseractOCRProtocol`, `LLMVisionProtocol`, `VideoProcessingProtocol`, `VideoAnalysisProtocol`, `ObjectTrackingProtocol`, `VideoUnderstandingProtocol`, `FFmpegVideoProtocol`, `WorkspaceProtocol`, `SystemConfigurationProtocol`, `SystemJobProtocol`, plus the aggregate facade `RegistryServiceAggregate`.
- **Business Rules**: Declarations only, without method bodies or business logic; every method signature uses taxonomy value objects rather than primitives; aggregates are composite entry points and are excluded from the capability-seam count.
- **Edge Cases**: A seam grows a second unrelated responsibility (split it into another protocol rather than widen one port); a method needs a primitive (wrap it in a value object).
- **Error Handling**: Contract declarations raise no behaviour of their own; failure semantics are stated by the taxonomy errors the signatures carry.

### FR-SHR-003: Provide the utility layer

- **Description**: Provide reusable, stateless, domain-agnostic functions.
- **Input**: Values, paths, and options supplied by callers in any layer.
- **Output**: Configuration load, merge, and serialize helpers; package and system binary availability checks; endpoint connectivity check; package version resolution; video frame extraction helpers; command output serialization helpers; pure image operations (grayscale, threshold, blur, edge, contour, histogram, optical flow); a synchronous bridge for coroutines; path normalization and executable validation.
- **Business Rules**: Stateless functions only — no classes, no instance state, no global mutable singletons; utilities depend on taxonomy and never on contracts, capabilities, agents, surfaces, or composition.
- **Edge Cases**: Missing package or binary; unreadable configuration file; coroutine that completes with an error; path with a trailing separator or symlinked segment.
- **Error Handling**: Availability checks report absence as a value rather than an exception; parsing helpers surface a typed taxonomy error naming the input that failed.

## API Contract

### Protocol API

| Method | Input | Output | Error | Event | Description |
|--------|-------|--------|-------|-------|-------------|
| `analyze_screenshot` | image path, optional prompt | analysis result | image processing error | none | Image processing port: analyse one screenshot |
| `extract_text` | image path, language code | OCR text | OCR error | none | OCR port shared by the image and Tesseract capabilities |
| `compare_screenshots` | two image paths | comparison report | comparison error | none | Image processing port: structural difference between two screenshots |
| `backend` | none | backend name | configuration error | none | Vision port: report the configured backend |
| `model` | none | model name | configuration error | none | Vision port: report the configured model |
| `analyze_image` | image path, prompt | analysis result | vision error | none | Vision port: send one image to the external endpoint |
| `get_info` | video path | video metadata | video processing error | none | Video port: stream metadata |
| `check_corruption` | video path | decodability flag | video processing error | none | Video port: decodability check |
| `extract_frames` | video path, sampling parameters | frame paths | frame extraction error | none | Video port: sample frames for analysis |
| `detect_scenes` | video path, threshold | scene boundary list | analysis error | none | Video analysis port: scene boundaries |
| `detect_motion` | video path, area threshold | motion events | analysis error | none | Video analysis port: motion events |
| `track_object` | video path, bounding box, frame budget | trajectory points | tracking error | none | Object tracking port: follow one object across frames |
| `analyze` | video path, prompt | understanding result | understanding error | none | Video understanding port: bounded key frame summary |
| `run` | argument list, output flag, timeout | command output | execution error | none | Media tool port: run one media command |
| `init_workspace` | target workspace directory | provisioning summary | workspace error | none | Workspace port: provision the XDG layout |
| `get_config` | optional configuration key | resolved value | configuration error | none | Configuration port: resolve by precedence |
| `set_config` | configuration key and value | overwrite confirmation | configuration error | none | Configuration port: persist one key |
| `get_status` | none | readiness report | readiness error | none | Job port: readiness and active job registry |
| `cancel_job` | job identifier | cancellation confirmation | cancellation error | none | Job port: cancel one registered operation |

### Aggregate API

| Method | Input | Output | Error | Event | Description |
|--------|-------|--------|-------|-------|-------------|
| `execute_in_process` | command name and keyword arguments | command output | command execution error | none | Single composite entry point every surface calls to run a domain command |

## Integration Points

| System | Direction | Purpose | Failure mode |
|--------|-----------|---------|--------------|
| Capabilities layer | in | Consume taxonomy types and utilities, and carry out the protocol ports | port not honoured -> composition error at startup |
| Agent layer | in | Implement the aggregate facade and call protocol ports | aggregate missing -> composition error at startup |
| Surface layer | in | Consume the aggregate facade, taxonomy types, and utilities | facade unavailable -> structured error to the caller |
| Root composition | in | Wire concrete implementations into the contracts | misconfigured wiring -> startup failure naming the port |
| Feature specifications | out | Fix the names, values, and error semantics every layer above reuses | term drift -> same word carrying two meanings |

## Non-functional Requirements

| Metric | Target | Measurement method |
|--------|--------|--------------------|
| Utility statefulness | zero in-memory mutable state | review of utility boundaries plus a state-reuse test |
| Value object immutability | every value object frozen after construction | construction-then-mutation test |
| Upper-layer imports | zero imports from capability, agent, surface, or composition layers | import audit of the shared module |
| Contract purity | zero method bodies in protocol and aggregate declarations | declaration review |
| Primitive leakage | zero primitives in entity, error, and event fields | type audit of taxonomy declarations |

## Test Scenarios

- Constructing a value object twice from equal input yields two instances that cannot be mutated afterwards.
- A utility called twice with equal input returns equal output and shares no state between calls.
- A protocol port with a primitive argument is rejected by the type audit and replaced by a value object.
- A utility that imports from a capability, agent, surface, or composition layer fails the import audit.
- An availability check on a missing binary reports absence as a value and raises no exception.

## Assumptions & Constraints

- The shared module is a cross-cutting kernel: it holds taxonomy, contract, and utility code only, and never capabilities, agents, or surfaces.
- All three layers ship in one module, so any change here reaches every feature at once and needs the full gate run.
- Primitive types are confined to value objects and constants; entities, errors, and events are typed with taxonomy value objects.
- Utility functions stay stateless; anything needing state belongs in a capability above.

## Glossary

- **Taxonomy layer**: The layer of value objects, errors, events, and constants every other layer may depend on.
- **Value object**: An immutable typed wrapper carrying one domain concept with its validation.
- **Protocol**: An abstract capability port that a capability implements and an agent calls.
- **Aggregate**: A composite facade exposing one entry point that coordinates several protocols.
- **Utility**: A stateless function usable from any layer with no dependency above taxonomy.
