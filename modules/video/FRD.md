# FRD — Video Intelligence

## Reference

- PRD: [PRD.md](../../PRD.md)
- Backlog: [BACKLOG.md](BACKLOG.md)

## System Overview

The video feature provides deterministic media processing plus optional vision-language-model-backed video understanding. The video orchestrator is a pure delegation facade: CLI and MCP surfaces dispatch a command name into the orchestrator, which routes it to injected processing, analysis, tracking, video-understanding, and media-adapter ports. The composition root wires the image vision adapter into the video-understanding port so that smart analysis reuses one VLM integration. OpenCV work runs through pure utility functions, and FFmpeg-backed checks run through a dedicated media port.

```text
CLI / MCP surface
        │
        ▼
Root composition
        │
        ▼
Video orchestrator
 ┌──────┼──────────────┬───────────────────┐
 ▼      ▼              ▼                 ▼
Process Analysis      Tracking       Understanding
 │      │              │                 │
FFmpeg  OpenCV       OpenCV         OpenCV + VLM
media   analysis     tracking       understanding
port    ports
```

## Functional Requirements

### FR-VID-001: Read video metadata

- **Description**: Return frame count, frame rate, dimensions, and related metadata for a readable video.
- **Input**: A video file path.
- **Output**: A structured video-metadata record serialised as JSON.
- **Business Rules**: The command runs through the video-processing port; numeric metadata is preserved inside the shared output model without reinterpretation.
- **Edge Cases**: Missing file, zero frame rate, invalid codec, empty video.
- **Error Handling**: A controlled processing error is returned when metadata cannot be read; no raw adapter exception reaches the surface.

### FR-VID-002: Extract frames

- **Description**: Extract frames from a video at a requested interval.
- **Input**: A video file path and a positive interval value.
- **Output**: A JSON list of generated image paths.
- **Business Rules**: The interval is positive and validated through the shared value object before extraction starts; the default interval is a shared constant.
- **Edge Cases**: Interval larger than video duration, invalid media, no readable frames.
- **Error Handling**: The capture resource is released and extraction failures are reported without leaving an open handle.

### FR-VID-003: Check corruption

- **Description**: Determine whether a video can be opened and decoded reliably.
- **Input**: A video file path.
- **Output**: A JSON object containing a `corrupted` flag.
- **Business Rules**: A missing or undecodable file must never be reported as healthy; the check runs through the video-processing port backed by the media port.
- **Edge Cases**: Empty file, partial file, unsupported codec, missing media tool.
- **Error Handling**: Adapter failures are normalised into a controlled result or an explicit runtime error carrying operation context.

### FR-VID-004: Detect scenes and motion

- **Description**: Detect scene transitions and motion events for downstream analysis.
- **Input**: A video file path, plus a scene threshold or a minimum motion area.
- **Output**: Structured lists of scene-change or motion-event records.
- **Business Rules**: Threshold values are positive and represented by shared value objects; defaults come from shared constants.
- **Edge Cases**: Static video, noisy video, very short video, no events.
- **Error Handling**: An empty list is returned for a valid video with no events; invalid media yields controlled errors.

### FR-VID-005: Track an object

- **Description**: Track an object through video frames starting from an initial bounding box.
- **Input**: A video path, a bounding box as `X,Y,W,H`, and an optional maximum frame count.
- **Output**: A JSON list of bounding boxes with frame or timestamp information.
- **Business Rules**: Bounding box coordinates and the maximum frame count are validated before the tracking port runs; width and height must be positive.
- **Edge Cases**: Bounding box outside the frame, object disappears, empty video, unsupported tracker.
- **Error Handling**: Tracking stops cleanly and the frames successfully tracked are returned.

### FR-VID-006: Analyze video with a vision-language model

- **Description**: Select representative key frames, analyse each frame, and synthesise a short summary.
- **Input**: A video path and an optional prompt.
- **Output**: A structured video-understanding record containing video metadata, sampling statistics, per-frame analyses, and a summary.
- **Business Rules**: Scene changes, top motion events, and uniform sampling contribute candidate frames; selection is capped at a bounded number of frames and the summary prompt is bounded; generated frame files are removed after execution.
- **Edge Cases**: No frames extracted, failed frame write, unavailable vision-language model, long video, empty analysis response, corrupted source video.
- **Error Handling**: Per-frame analysis failures become fallback frame descriptions; summary failures fall back to joined frame descriptions; media resources are always released.

## API Contract

### Protocol API

| Method | Input | Output | Error | Event | Description |
|---|---|---|---|---|---|
| `get_info` | video path | video metadata record | controlled processing error | — | Read structural video metadata |
| `extract_frames` | video path, interval | list of generated image paths | controlled extraction error | — | Sample frames at an interval |
| `check_corruption` | video path | corruption flag | controlled media error | — | Validate decodability |
| `detect_scenes` | video path, scene threshold | list of scene-change records | controlled analysis error | — | Detect scene transitions |
| `detect_motion` | video path, minimum motion area | list of motion-event records | controlled analysis error | — | Detect motion events |
| `track_object` | video path, bounding box, max frames | list of tracked bounding boxes | controlled tracking error | — | Track an object from an initial box |
| `analyze` | video path, prompt, optional config | structured video understanding | controlled understanding error | — | Bounded VLM video understanding |

### Aggregate API

| Method | Input | Output | Error | Event | Description |
|---|---|---|---|---|---|
| `execute` | command name, command arguments | command output | controlled command error | — | Single composite dispatch over all video commands |

## Integration Points

| System | Direction | Purpose | Failure mode |
|---|---|---|---|
| Media tooling (FFmpeg) | outbound | Video metadata reads and corruption checks | Missing tool or decode failure → controlled media error result |
| OpenCV utilities | internal | Frame capture, decoding, scene and motion pure functions | Undecodable frame set → controlled processing error |
| External VLM | outbound | Per-frame descriptions and summary synthesis for smart analysis | Unreachable endpoint → fallback frame descriptions |
| Composition root | inbound | Wires the image VLM adapter into video understanding | Missing adapter → smart analysis unavailable, deterministic commands still work |
| CLI surface | inbound | Exposes all video commands as subcommands | Unknown command name → controlled command error |
| MCP surface | inbound | Exposes all video commands through execution and discovery | Missing tool capability → controlled execution error |

## Non-functional Requirements

| Metric | Target | Measurement method |
|---|---|---|
| Bounded smart-analysis work | At most 12 frames sent to the VLM per analysis | Assert the sampling count never exceeds the bound |
| Resource safety | No open capture handles after a command; temporary frame directories removed | Inspect open file handles and the temporary directory after each run |
| Failure isolation | One frame's analysis failure never discards other frames' results | Inject a failing VLM response for one frame and verify remaining results |
| Determinism | Core commands run without a live VLM endpoint | Run deterministic commands with no endpoint configured |
| Orchestrator purity | The orchestrator delegates to injected ports only, with no domain logic | Review the orchestrator for direct capability or media calls |
| Observability | Media and VLM failures carry operation context | Verify returned errors name the failing operation |

## Test Scenarios

- Read metadata from a generated valid video and verify the structured output.
- Extract frames with a normal interval and with an interval larger than the video duration.
- Detect corruption for a valid, missing, and malformed file.
- Detect scenes and motion in static and changing videos; verify empty results for static media.
- Track an object with a valid bounding box and handle an invalid bounding box.
- Run smart-video analysis with a stubbed VLM and verify the structured output.
- Verify smart-video sampling never exceeds the frame cap.
- Verify per-frame VLM failure produces fallback descriptions.
- Verify generated frame paths do not exist after smart-video analysis returns.
- Verify every video command is present in both the CLI parser and MCP discovery.

## Assumptions & Constraints

- Smart-video analysis assumes a configured OpenAI-compatible VLM endpoint; the deterministic commands remain usable without it.
- Long videos are summarised from a bounded representative sample rather than analysed frame by frame.
- Tuning parameters (extraction interval, scene threshold, minimum motion area, maximum tracked frames) are locked internal constants; public surfaces do not expose them.
- Generated frame images are temporary working data and must not persist after analysis.

## Glossary

- **Key frame**: A selected frame representative of a scene, motion event, or uniform sample.
- **VLM**: Vision-language model used for per-frame and video-level analysis.
- **Timeline**: A structured sequence of sampled video events.
- **Bounding box**: A rectangular region `X,Y,W,H` marking an object's position in a frame.
