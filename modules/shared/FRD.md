# FRD — Shared Foundation (Taxonomy, Contract, Utility)

## System Overview

The `shared` module is the foundation layer for Vision Arwaky. In compliance with the Agentic Engineering System (AES), it contains **Taxonomy**, **Contract**, and **Utility** layers only. It does not contain capabilities, agents, surfaces, or root composition concerns.

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
      │ │ Contract Layer (ABCs)   │ │
      │ └─────────────────────────┘ │
      │ ┌─────────────────────────┐ │
      │ │ Utility Layer (Pure Fn) │ │
      │ └─────────────────────────┘ │
      │ ┌─────────────────────────┐ │
      │ │ Taxonomy Layer (VOs)    │ │
      │ └─────────────────────────┘ │
      └─────────────────────────────┘
```

## Functional Requirements

### FR-SHR-001: Taxonomy Layer
- **Description:** Provide immutable, domain-stable value objects, errors, events, and constants.
- **Components:**
  - `taxonomy_command_vo.py`: Defines `CommandDomain` enum (`IMAGE`, `VIDEO`, `SYSTEM`) and routing classification sets (`IMAGE_COMMANDS`, `VIDEO_COMMANDS`, `SYSTEM_COMMANDS`, `ALL_COMMANDS`).
  - `taxonomy_vision_vo.py`: Core value objects (`AnalysisPrompt`, `BoundingBox`, `CommandName`, `CommandOutput`, `FilePath`, `IntervalSeconds`, `VideoInfo`, `VisionAnalysis`, `VideoUnderstanding`, etc.).
  - `taxonomy_xdg_paths_vo.py`: Standard XDG directory paths (`config_dir`, `data_dir`, `cache_dir`, `state_dir`, `bin_dir`).
  - `taxonomy_vision_constant.py`: Tunable constants (`DEFAULT_VLM_TIMEOUT_S`, `SCENE_THRESHOLD`, `MIN_MOTION_AREA`, `EMBEDDED_SKILL_MD`).
  - `taxonomy_vision_error.py`: Domain exception hierarchy (`VisionDomainError`, `ImageProcessingError`, `VideoProcessingError`, `InvalidParameterError`).
  - `taxonomy_vision_event.py`: Domain events (`SceneChange`, `MotionEvent`).
- **Rules:** Zero dependencies on upper layers; primitive types allowed only in VOs and constants.

### FR-SHR-002: Contract Layer
- **Description:** Provide pure abstract base class (ABC) definitions for protocols and aggregates.
- **Components:**
  - `contract_registry_service_aggregate.py`: Aggregate facade interface `RegistryServiceAggregate`.
  - Feature Protocols: `ImageProcessingProtocol`, `TesseractOCRProtocol`, `LLMVisionProtocol`, `VideoProcessingProtocol`, `VideoAnalysisProtocol`, `ObjectTrackingProtocol`, `VideoUnderstandingProtocol`, `FFmpegVideoProtocol`, `WorkspaceProtocol`, `SystemConfigurationProtocol`, `SystemJobProtocol`.
- **Rules:** Pure abstract declarations without method bodies or business logic.

### FR-SHR-003: Utility Layer
- **Description:** Reusable, stateless, domain-agnostic pure functions.
- **Components:**
  - `utility_config_handler.py`: XDG-aware configuration loader, merger, and serializer.
  - `utility_dependency_checker.py`: Python package and system binary availability inspector.
  - `utility_llm_check.py`: OpenAI-compatible endpoint connectivity checker.
  - `utility_version.py`: Package version resolver.
  - `utility_frame_extractor.py`: OpenCV video frame extractor helpers.
  - `utility_command_output.py`: CommandOutput VO serialization helpers.
  - `utility_opencv_ops.py`: Pure OpenCV wrappers (grayscale, threshold, blur, edge, contour, histogram, optical flow).
  - `utility_async_runner.py`: Synchronous bridge for coroutines.
  - `utility_system_utils.py`: Path normalization and executable validation.
- **Rules:** Stateless functions only; no `class`, no instance state, no global mutable singletons.

## Integration Points

| Consumer Layer | Used Shared Components |
|---|---|
| Capabilities | Implements Contract Protocols; consumes Taxonomy VOs and Utilities |
| Agent | Implements Contract Aggregates; calls Protocols; consumes Taxonomy VOs and Utilities |
| Surface | Consumes Contract Aggregates, Taxonomy VOs, and Utilities |
| Root | Wires implementations conforming to Contract protocols and aggregates |

## Non-functional Requirements

- **Statelessness:** Utilities must not maintain in-memory mutable state.
- **Immutability:** Value Objects in taxonomy must be immutable (Pydantic frozen models or enums).
- **Zero Upper-Layer Imports:** Shared files must never import from `image`, `video`, `system`, `cli`, `mcp`, or `root`.
