# FRD — Video Intelligence

## Feature Overview

The video feature provides bounded smart-video understanding via vision-language model. The video orchestrator is a pure delegation facade: CLI and MCP surfaces dispatch a command name into the orchestrator, which routes it to the video-understanding port. OpenCV work runs through pure utility functions, and the composition root wires the image vision adapter into the video-understanding port so that smart analysis reuses one VLM integration.

## Functional Requirements

### FR-VID-001: Analyze video with a vision-language model

**Description:** Select representative key frames, analyse each frame, and synthesise a short summary.

#### Business Logic

- Uniform sampling contributes candidate frames; selection is capped at a bounded number of frames and the summary prompt is bounded; generated frame files are removed after execution.

#### Edge Cases

- No frames extracted, failed frame write, unavailable vision-language model, long video, empty analysis response, corrupted source video.

#### Technical Specification

| Aspect | Detail |
|--------|--------|
| **Input** | `video` path and an optional `prompt`, plus optional `VideoUnderstandingConfig`. Source: caller command request. |
| **Output** | Structured `VideoUnderstanding` record containing video metadata, sampling statistics, per-frame analyses, and a summary. Destination: caller. |
| **Protocol** | `IVideoUnderstandingProtocol` |
| **Method** | `analyze` |
| **Event** | None |
| **Error** | Per-frame analysis failures become fallback frame descriptions; summary failures fall back to joined frame descriptions; media resources are always released. |

#### Test

| Context | When Action | Then Observable Result |
|---------|-------------|------------------------|
| Valid video with stubbed VLM | `analyze-video` is invoked | Structured understanding record is returned |
| Unavailable VLM endpoint | `analyze-video` is invoked | Fallback frame descriptions are returned |
| Smart analysis completes | `analyze-video` is invoked | Generated frame files no longer exist |
| Frame count exceeds cap | `analyze-video` is invoked | At most 12 frames are sent to the VLM |

#### Metric

| Target Metric | Value |
|---------------|-------|
| Max Frames Sent to VLM | 12 |
| Summary Prompt Bound (chars) | 12000 |
| Frames Surviving After Analysis | 0 |

## Public Interface

| Aspect | Detail |
|--------|--------|
| Agent | `VideoOrchestrator` |
| Aggregate | `IRegistryServiceAggregate` |
| Method | `execute_in_process` |
| Request | `CommandName` and `SystemCommandParams` (`analyze-video`) |
| Response | `CommandOutput` |

## Reference

| Artifact | Purpose | Link |
|----------|---------|------|
| PRD | Business goals, user stories, and scope | [PRD.md](../../PRD.md) |
| Backlog | Task tracking, epics, and implementation status | [BACKLOG.md](BACKLOG.md) |
| Roadmap | Timeline, phasing, and dependencies | [ROADMAP.md](../../ROADMAP.md) |
| Architecture | System boundaries, tech stack, and infrastructure | [ARCHITECTURE.md](../../ARCHITECTURE.md) |