# FRD — Image Intelligence

## Feature Overview

The image feature sits in the feature layer, invoked by the CLI and MCP surfaces through the image aggregate. It coordinates image analysis through the vision-language adapter behind contracts. Deterministic pixel operations are pure utility functions; vision analysis calls the external endpoint behind an adapter.

## Functional Requirements

### FR-IMG-001: Analyze image

**Description:** Analyze a supplied image with the configured vision-language model and return structured text or a deterministic fallback result.

#### Business Logic

- The image path must pass through the dispatcher before any analysis runs.
- The vision adapter must use the configured endpoint and model settings.
- Deterministic operations must not require a network call.

#### Edge Cases

- Missing image, unsupported image format, empty model response, unreachable model endpoint, malformed model response.

#### Technical Specification

| Aspect | Detail |
|--------|--------|
| **Input** | `image` path and optional `prompt`. Source: caller command request. |
| **Output** | JSON containing the analysis source and the returned text, wrapped in the command output envelope. Destination: caller. |
| **Protocol** | `ILLMVisionProtocol` |
| **Method** | `analyze` |
| **Event** | None |
| **Error** | Controlled command error or the deterministic fallback result; never a raw network exception. |

#### Test

| Context | When Action | Then Observable Result |
|---------|-------------|------------------------|
| Valid image with reachable vision adapter | `analyze` is invoked | Structured analysis result is returned |
| Valid image with unreachable vision endpoint | `analyze` is invoked | Deterministic fallback result is returned |
| Missing image path | `analyze` is invoked | Controlled command error is raised |

#### Metric

| Target Metric | Value |
|---------------|-------|
| Fallback Rate on Endpoint Failure | 100% |
| Raw Network Exceptions Exposed | 0 |

### FR-IMG-002: Analyze screenshot

**Description:** Analyze a supplied screenshot image with the image-processing capability and return structured `VisionAnalysis` output.

#### Business Logic

- The image path must pass through the dispatcher before any analysis runs.
- The image-processing capability wraps the VLM adapter behind the `IImageProcessingProtocol` seam.
- Deterministic operations must not require a network call.

#### Edge Cases

- Missing image, unsupported image format, empty model response, unreachable model endpoint, malformed model response.

#### Technical Specification

| Aspect | Detail |
|--------|--------|
| **Input** | `image` path and optional `prompt`. Source: caller command request. |
| **Output** | Structured `VisionAnalysis` record containing source, text, model name, and optional error. Destination: caller. |
| **Protocol** | `IImageProcessingProtocol` |
| **Method** | `analyze_screenshot` |
| **Event** | None |
| **Error** | Controlled command error or the deterministic fallback result; never a raw network exception. |

#### Test

| Context | When Action | Then Observable Result |
|---------|-------------|------------------------|
| Valid image with reachable VLM adapter | `analyze_screenshot` is invoked | Structured `VisionAnalysis` result is returned |
| Valid image with unreachable vision endpoint | `analyze_screenshot` is invoked | Deterministic fallback result is returned |
| Missing image path | `analyze_screenshot` is invoked | Controlled command error is raised |

#### Metric

| Target Metric | Value |
|---------------|-------|
| Fallback Rate on Endpoint Failure | 100% |
| Raw Network Exceptions Exposed | 0 |

## Public Interface

| Aspect | Detail |
|--------|--------|
| Agent | `ImageOrchestrator` |
| Aggregate | `IImageProcessingAggregate` |
| Method | `execute` |
| Request | `ImageRequest` (`Analyze`) |
| Response | `CommandOutput` |

## Reference

| Artifact | Purpose | Link |
|----------|---------|------|
| PRD | Business goals, user stories, and scope | [PRD.md](../../PRD.md) |
| Backlog | Task tracking, epics, and implementation status | [BACKLOG.md](BACKLOG.md) |
| Roadmap | Timeline, phasing, and dependencies | [ROADMAP.md](../../ROADMAP.md) |
| Architecture | System boundaries, tech stack, and infrastructure | [ARCHITECTURE.md](../../ARCHITECTURE.md) |