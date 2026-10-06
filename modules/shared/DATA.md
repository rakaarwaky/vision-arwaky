# DATA — Shared Foundation (Taxonomy, Contract, Utility)

## Reference

- PRD: [PRD.md](../../PRD.md)
- FRD: [FRD.md](FRD.md)
- Backlog: [BACKLOG.md](BACKLOG.md)

## Data Overview

The `shared` module is the kernel of the workspace. It holds the three
foundation layers every feature depends on, and nothing above them.

| Layer | Prefix | Role |
|---|---|---|
| Taxonomy | `taxonomy_` | Immutable VOs, errors, events, constants |
| Contract | `contract_` | ABC protocol and aggregate interfaces |
| Utility | `utility_` | Stateless pure functions |

## Data Domain

| Group | Files |
|---|---|
| Taxonomy | `taxonomy_command_vo`, `taxonomy_vision_vo`, `taxonomy_xdg_paths_vo`, `taxonomy_vision_constant`, `taxonomy_vision_error`, `taxonomy_vision_event` |
| Contract | `contract_registry_service_aggregate`, `contract_image_processing_protocol`, `contract_tesseract_ocr_protocol`, `contract_llm_vision_protocol`, `contract_video_processing_protocol`, `contract_video_analysis_protocol`, `contract_object_tracking_protocol`, `contract_video_understanding_protocol`, `contract_ffmpeg_video_protocol`, `contract_workspace_protocol`, `contract_system_configuration_protocol`, `contract_system_job_protocol` |
| Utility | `utility_config_handler`, `utility_dependency_checker`, `utility_llm_check`, `utility_version_resolver`, `utility_frame_extractor`, `utility_command_output`, `utility_opencv_ops`, `utility_async_runner`, `utility_system_utils`, `utility_xdg_paths` |

## Assumptions & Constraints

- Zero upper-layer imports: shared files never import from `image`, `video`,
  `system`, `cli`, `mcp`, or root.
- Utilities are stateless: no classes, no mutable globals.
- Protocols are pure ABCs: abstract methods only, no business logic.

Features import shared types downward only:
`root → surface → agent → capabilities → contract/utility/taxonomy`.
No consumer may import a shared file into another feature's source without
routing through a shared contract or utility symbol.
