# PRD — Vision Arwaky

## Problem Statement

AI agents and developers often need a reliable local service for inspecting images and videos, extracting text, understanding visual scenes, and performing deterministic computer-vision operations. Existing workflows frequently split these capabilities across unrelated scripts, external tools, and ad-hoc model integrations. Vision Arwaky provides one Python package, one CLI, and one MCP server that expose these capabilities through a consistent dependency-injected architecture.

The product is designed for local-first operation. Deterministic operations such as metadata extraction, frame sampling, OCR, motion detection, scene detection, comparison, and tracking should remain useful without a language model. Vision-language analysis is an optional enhancement supplied by an OpenAI-compatible external endpoint.

## Product Vision

Vision Arwaky will be a dependable visual-intelligence utility for AI agents and technical users. A caller should be able to send a supported image or video command through the CLI or MCP interface, receive structured output, and understand failures without needing to know the internal adapter graph.

## Goals and Success Metrics

| Goal | Success metric |
|---|---|
| Provide a stable image and video command surface | All documented CLI commands are registered and covered by parser or integration tests |
| Support agent integration | The MCP server exposes six stable tools and discovers all supported image and video commands |
| Keep deterministic processing local and reproducible | The full test suite passes on Python 3.12 and 3.13 with required system tools installed |
| Keep architecture maintainable | Ruff, Mypy, package build, and AES self-lint pass with zero violations |
| Make smart video analysis bounded | Key-frame sampling is capped, temporary artifacts are cleaned up, and summary prompts have a bounded size |
| Support practical local deployment | `uv sync`, the documented system dependencies, and the package entry points (`va`, `vision-arwaky-cli`, `vision-arwaky-mcp`, `vision-arwaky-tui`) are sufficient to start the project |

## User Personas

### AI Agent Developer

An engineer integrating image and video capabilities into an agent through MCP. This user needs discoverable command names, stable JSON output, predictable error responses, and a status tool that reports missing dependencies.

### Computer-Vision Developer

A developer using the CLI to inspect media files, run OCR, track objects, compare screenshots, or generate video timelines. This user needs clear command arguments, local reproducibility, and useful diagnostic output.

### QA and Automation Engineer

A user building automated checks around media fixtures. This user needs deterministic commands, bounded resource usage, machine-readable results, and a test workflow that can run in CI without a live VLM endpoint.

### Technical Maintainer

A maintainer reviewing architectural changes. This user needs explicit layer boundaries, dependency-injection wiring, quality gates, and documentation that maps product behavior to feature modules.

## Scope

### In scope

The product includes the following capabilities:

| Area | Included functionality |
|---|---|
| Workspace & System | Workspace initialization, XDG directory layout, SKILL guide embedding, configuration management, and job lifecycle |
| Image analysis | VLM-backed image analysis with a deterministic fallback |
| OCR | Text extraction through Tesseract |
| Image inspection | Screenshot comparison with perceptual hashing and bounding diffs |
| Video processing | Metadata extraction, frame extraction, and corruption checks |
| Video analysis | Scene changes, motion events, and object tracking |
| Smart video understanding | Bounded key-frame selection, per-frame VLM analysis, and summary generation |
| Agent integration | MCP tools for workspace init, execution, discovery, help, status, and cancellation |
| Local operation | Configuration through repository or user config with FFmpeg, Tesseract, and OpenCV support |
| Maintainability | AES architecture, typed contracts, DI composition roots, tests, and CI quality gates |

### Out of scope

The current product does not include visual-memory storage or search commands, a hosted SaaS control plane, user accounts, cloud media storage, deep-learning object detection, model training, or a bundled vision-language model.

## Feature Requirements

### P0 — Must Have

- [ ] The CLI must expose `init`, `analyze`, `ocr`, `compare`, `video-info`, `extract-frames`, `check-corruption`, `detect-scenes`, `detect-motion`, `track`, and `analyze-video`.
- [ ] The MCP server must expose `vision_init`, `vision_execute`, `vision_list_commands`, `vision_help`, `vision_status`, and `vision_cancel`.
- [ ] `vision_list_commands` must list every supported workspace, image, and video command.
- [ ] Every public execution path must route through modular domain containers and orchestrators.
- [ ] Smart-video analysis must cap selected frames, bound summary prompt size, and remove temporary frame files after execution.
- [ ] The package must build and the complete test suite must pass on supported Python versions.
- [ ] The self-lint scan must finish with zero violations.

### P1 — Should Have

- [ ] Image and video command outputs should be JSON-serializable and stable enough for agent consumption.
- [ ] The status tool should distinguish missing Python packages, missing system binaries, and unavailable VLM configuration.
- [ ] Smart-video tests should cover empty media, VLM failure fallback, frame sampling bounds, and cleanup behavior.
- [ ] Documentation should remain synchronized across the PRD, feature FRDs, README, and agent-facing skill reference.
- [ ] CLI errors should identify invalid paths, missing dependencies, unsupported commands, and unreachable VLM endpoints clearly.

### P2 — Nice to Have

- [ ] Add configurable concurrency for independent per-frame VLM requests.
- [ ] Add a streaming or incremental summary mode for long videos.
- [ ] Add optional structured schemas for command-specific outputs.
- [ ] Add performance benchmarks for frame extraction, OCR, and bounded smart-video analysis.

## Non-functional Requirements

| Category | Requirement |
|---|---|
| Compatibility | Python 3.12 and 3.13 are supported in CI. |
| Performance | Deterministic media operations should not require a VLM. Smart-video analysis must use bounded frame and prompt limits. |
| Reliability | Temporary files must be cleaned up, failed frame writes must be handled, and external VLM failures must produce a controlled fallback or error. |
| Security | User-provided paths must not be passed through shell evaluation. External endpoint configuration must remain outside committed secrets. |
| Maintainability | Feature modules communicate through contracts and constructor injection; surfaces must not instantiate capabilities directly. |
| Observability | Errors should be logged with enough context to identify the operation and external dependency involved. |
| Packaging | `uv build` must produce a valid source distribution and wheel. |

## Product Architecture

The implementation uses seven AES layers: taxonomy, contract, utility, capabilities, agent, surface, and root. Feature-specific details are documented in the feature FRDs:

- [Shared FRD](modules/shared/FRD.md)
- [System FRD](modules/system/FRD.md)
- [Image FRD](modules/image/FRD.md)
- [Video FRD](modules/video/FRD.md)
- [CLI FRD](modules/cli/FRD.md)
- [MCP FRD](modules/mcp/FRD.md)

The shared contracts and value objects are supporting infrastructure for these features rather than an independent user-facing feature.

## Risks and Open Questions

| Risk or question | Mitigation or decision |
|---|---|
| External VLM endpoint may be unavailable | Keep deterministic fallbacks and return controlled errors; document the endpoint requirement. |
| Long videos may create too many VLM requests | Enforce a maximum key-frame count and summary prompt limit. |
| Media codecs vary by environment | Require FFmpeg and OpenCV runtime dependencies and test with generated fixtures. |
| External dependency APIs may change | Keep adapters behind contracts and use explicit timeout and response handling. |
| Configuration may contain machine-specific paths | Prefer user configuration and avoid committing credentials or model files. |
| Feature and docs may drift | Treat FRDs and README command tables as part of the same change as public behavior. |

## Acceptance Criteria

A release candidate satisfies this PRD when the documented CLI and MCP surfaces match the implementation, feature FRDs describe the active contracts and edge cases, `bash scripts/gates.sh` passes, `uv build` succeeds, and smart-video analysis remains bounded and cleans up its generated artifacts.

## References

- [README.md](README.md)
- [SKILL.md](SKILL.md)
- [add-docs-python skill](.agents/skills/add-docs-python/SKILL.md)
