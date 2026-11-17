# FRD — Video Intelligence

## Feature Overview

The video feature provides deterministic media processing plus optional vision-language-model-backed video understanding. The video orchestrator is a pure delegation facade: CLI and MCP surfaces dispatch a command name into the orchestrator, which routes it to injected processing, analysis, tracking, video-understanding, and media-adapter ports. The composition root wires the image vision adapter into the video-understanding port so that smart analysis reuses one VLM integration. OpenCV work runs through pure utility functions, and FFmpeg-backed checks run through a dedicated media port.

## Functional Requirements

### FR-VID-001: Read metadata and extract frames

**Description:** Return frame count, frame rate, dimensions, and related metadata for a readable video, and extract frames at a requested interval.

#### Business Logic

- The command runs through the video-processing port; numeric metadata is preserved inside the shared output model without reinterpretation.
- The interval is positive and validated through the shared value object before extraction starts; the default interval is a shared constant.

#### Edge Cases

- Missing file, zero frame rate, invalid codec, empty video, interval larger than video duration, no readable frames.

#### Technical Specification

| Aspect | Detail |
|--------|--------|
| **Input** | `video` file path and optional positive `interval` value (default `FRAME_EXTRACTION_INTERVAL_S`). Source: caller command request. |
| **Output** | Structured `VideoInfo` record or JSON list of generated image paths, serialised in the command output envelope. Destination: caller. |
| **Protocol** | `IVideoProcessingProtocol` |
| **Method** | `get_info`, `extract_frames` |
| **Event** | None |
| **Error** | A controlled processing error is returned when metadata cannot be read; the capture resource is released and extraction failures are reported without leaving an open handle. |

#### Test

| Context | When Action | Then Observable Result |
|---------|-------------|------------------------|
| Valid readable video | `video-info` is invoked | Structured metadata record is returned |
| Missing or undecodable file | `video-info` is invoked | Controlled processing error is raised |
| Normal interval | `extract-frames` is invoked | JSON list of generated image paths is returned |
| Interval larger than video duration | `extract-frames` is invoked | Bounded frame set is returned without error |

#### Metric

| Target Metric | Value |
|---------------|-------|
| Raw Adapter Exceptions Reaching Surface | 0 |
| Metadata Numeric Fidelity | 100% |
| Extraction Frame Cap | 30 |
| Open Handles After Command | 0 |

### FR-VID-002: Check corruption

**Description:** Determine whether a video can be opened and decoded reliably.

#### Business Logic

- A missing or undecodable file must never be reported as healthy; the check runs through the video-processing port backed by the media port.

#### Edge Cases

- Empty file, partial file, unsupported codec, missing media tool.

#### Technical Specification

| Aspect | Detail |
|--------|--------|
| **Input** | `video` file path. Source: caller command request. |
| **Output** | JSON object containing a `corrupted` flag. Destination: caller. |
| **Protocol** | `IVideoProcessingProtocol` |
| **Method** | `check_corruption` |
| **Event** | None |
| **Error** | Adapter failures are normalised into a controlled result or an explicit runtime error carrying operation context. |

#### Test

| Context | When Action | Then Observable Result |
|---------|-------------|------------------------|
| Valid decodable video | `check-corruption` is invoked | `corrupted=false` is returned |
| Missing or malformed file | `check-corruption` is invoked | `corrupted=true` is returned |

#### Metric

| Target Metric | Value |
|---------------|-------|
| Healthy Reported on Undecodable File | 0 |
| Errors Carrying Operation Context | 100% |

### FR-VID-003: Detect scenes and motion

**Description:** Detect scene transitions and motion events for downstream analysis.

#### Business Logic

- Threshold values are positive and represented by shared value objects; defaults come from shared constants.

#### Edge Cases

- Static video, noisy video, very short video, no events.

#### Technical Specification

| Aspect | Detail |
|--------|--------|
| **Input** | `video` file path plus a scene `threshold` or a minimum motion `min_area` (defaults `SCENE_THRESHOLD`, `MIN_MOTION_AREA`). Source: caller command request. |
| **Output** | Structured lists of `SceneChange` or `MotionEvent` records as JSON. Destination: caller. |
| **Protocol** | `IVideoAnalysisProtocol` |
| **Method** | `detect_scenes`, `detect_motion` |
| **Event** | None |
| **Error** | An empty list is returned for a valid video with no events; invalid media yields controlled errors. |

#### Test

| Context | When Action | Then Observable Result |
|---------|-------------|------------------------|
| Changing video | `detect-scenes` is invoked | List of scene-change records is returned |
| Static video | `detect-scenes` is invoked | Empty list is returned |
| Changing video | `detect-motion` is invoked | List of motion-event records is returned |
| Static video | `detect-motion` is invoked | Empty list is returned |

#### Metric

| Target Metric | Value |
|---------------|-------|
| Events on Static Media | 0 |
| Defaults from Shared Constants | 100% |

### FR-VID-004: Track an object

**Description:** Track an object through video frames starting from an initial bounding box.

#### Business Logic

- Bounding box coordinates and the maximum frame count are validated before the tracking port runs; width and height must be positive.

#### Edge Cases

- Bounding box outside the frame, object disappears, empty video, unsupported tracker.

#### Technical Specification

| Aspect | Detail |
|--------|--------|
| **Input** | `video` path, a `bbox` as `X,Y,W,H`, and an optional `max_frames` (default `MAX_TRACK_FRAMES`). Source: caller command request. |
| **Output** | JSON list of bounding boxes with frame or timestamp information. Destination: caller. |
| **Protocol** | `IObjectTrackingProtocol` |
| **Method** | `track_object` |
| **Event** | None |
| **Error** | Tracking stops cleanly and the frames successfully tracked are returned. |

#### Test

| Context | When Action | Then Observable Result |
|---------|-------------|------------------------|
| Valid bounding box | `track` is invoked | List of tracked bounding boxes is returned |
| Invalid bounding box | `track` is invoked | Controlled `InvalidParameterError` is raised |

#### Metric

| Target Metric | Value |
|---------------|-------|
| Max Frames Tracked | 300 |
| Clean Stops on Lost Object | 100% |

### FR-VID-005: Analyze video with a vision-language model

**Description:** Select representative key frames, analyse each frame, and synthesise a short summary.

#### Business Logic

- Scene changes, top motion events, and uniform sampling contribute candidate frames; selection is capped at a bounded number of frames and the summary prompt is bounded; generated frame files are removed after execution.

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
| Request | `CommandName` and `SystemCommandParams` (`video-info`, `extract-frames`, `check-corruption`, `detect-scenes`, `detect-motion`, `track`, `analyze-video`) |
| Response | `CommandOutput` |

## Reference

| Artifact | Purpose | Link |
|----------|---------|------|
| PRD | Business goals, user stories, and scope | [PRD.md](../../PRD.md) |
| Backlog | Task tracking, epics, and implementation status | [BACKLOG.md](BACKLOG.md) |
| Roadmap | Timeline, phasing, and dependencies | [ROADMAP.md](../../ROADMAP.md) |
| Architecture | System boundaries, tech stack, and infrastructure | [ARCHITECTURE.md](../../ARCHITECTURE.md) |