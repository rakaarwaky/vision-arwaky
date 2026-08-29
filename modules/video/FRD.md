# FRD — Video Intelligence

## System Overview

The video feature provides deterministic media processing and optional VLM-backed smart video understanding. `VideoOrchestrator` delegates commands to injected processing, analysis, timeline, tracking, OpenCV, FFmpeg, and video-understanding ports. `root_video_container.py` composes the graph and the global root connects the image VLM adapter to the video-understanding capability.

```text
CLI / MCP surface
        │
        ▼
RootDispatcher
        │
        ▼
VideoOrchestrator
 ┌──────┼────────┬──────────┬──────────────┐
 ▼      ▼        ▼          ▼              ▼
Process Analysis Timeline Tracking  Understanding
 │      │        │          │              │
FFmpeg OpenCV   OpenCV    OpenCV      OpenCV + VLM
```

Primary implementation modules are under `modules/video/src/`:

| Module | Responsibility |
|---|---|
| `agent_video_orchestrator.py` | Routes video commands through injected ports |
| `capabilities_video_processor.py` | Metadata, extraction, conversion, GIF, and corruption operations |
| `capabilities_video_analyzer.py` | Scene and motion analysis |
| `capabilities_object_tracker.py` | Object tracking from an initial bounding box |
| `capabilities_timeline_generator.py` | Generates structured video timelines |
| `capabilities_video_understanding.py` | Selects bounded key frames, calls the VLM, and synthesizes a summary |
| `capabilities_ffmpeg_adapter.py` | Adapts FFmpeg operations |
| `root_video_container.py` | Builds the video dependency graph |

## Functional Requirements

### FR-VID-001: Read video metadata

- **Description:** Return frame count, FPS, dimensions, and related metadata for a readable video.
- **Input:** `video` path.
- **Output:** JSON metadata object.
- **Business rules:** The command must use the video-processing port and preserve numeric metadata in the shared output model.
- **Edge cases:** Missing file, zero FPS, invalid codec, empty video.
- **Error handling:** Return a controlled processing error when metadata cannot be read.

### FR-VID-002: Extract frames

- **Description:** Extract frames at a requested interval.
- **Input:** `video` path and interval value.
- **Output:** JSON list of generated image paths.
- **Business rules:** The interval must be positive and validated through the shared value object.
- **Edge cases:** Interval larger than video duration, invalid media, no readable frames.
- **Error handling:** Release the capture resource and report extraction failures without leaving an open handle.

### FR-VID-003: Convert and create GIF

- **Description:** Convert a video to another format or create a GIF for an optional time segment.
- **Input:** Input video, output path, and optional start/duration for GIF creation.
- **Output:** JSON success result.
- **Business rules:** Output paths are passed to the adapter as validated file-path values.
- **Edge cases:** Existing output, invalid segment, missing FFmpeg, unsupported codec.
- **Error handling:** Return a controlled adapter error and preserve the source video.

### FR-VID-004: Check corruption

- **Description:** Determine whether a video can be opened and decoded reliably.
- **Input:** `video` path.
- **Output:** JSON object containing `corrupted`.
- **Business rules:** A missing or undecodable file must not be reported as healthy.
- **Edge cases:** Empty file, partial file, unsupported codec, missing FFmpeg.
- **Error handling:** Normalize adapter failures into a controlled result or explicit runtime error.

### FR-VID-005: Detect scenes and motion

- **Description:** Detect scene transitions and motion events for downstream analysis.
- **Input:** `video` path, scene threshold or minimum motion area.
- **Output:** Lists of structured scene or motion event records.
- **Business rules:** Threshold values must be positive and represented by shared value objects.
- **Edge cases:** Static video, noisy video, very short video, no events.
- **Error handling:** Return an empty list for a valid video with no events and controlled errors for invalid media.

### FR-VID-006: Track an object

- **Description:** Track an object through video frames starting from an initial bounding box.
- **Input:** `video`, `bbox` as `X,Y,W,H`, and optional maximum frame count.
- **Output:** JSON list of bounding boxes with frame or timestamp information.
- **Business rules:** Bounding box coordinates and maximum frames must be validated before the tracking adapter runs.
- **Edge cases:** Bounding box outside the frame, object disappears, empty video, unsupported tracker.
- **Error handling:** Stop tracking cleanly and return the frames successfully tracked.

### FR-VID-007: Generate a timeline

- **Description:** Produce a structured timeline from sampled video content.
- **Input:** `video` and interval.
- **Output:** Timeline model serialized as JSON.
- **Business rules:** Timeline generation uses injected processing and analysis capabilities rather than direct surface-level implementation.
- **Edge cases:** No scenes, no motion, long videos, media with variable FPS.
- **Error handling:** Return a controlled result with available events or a diagnostic error.

### FR-VID-008: Analyze video with a VLM

- **Description:** Select representative key frames, analyze each frame, and synthesize a short summary.
- **Input:** `video`, optional prompt, interval, scene threshold, and minimum motion area.
- **Output:** `VideoUnderstanding` containing video metadata, sampling statistics, per-frame analyses, and a summary.
- **Business rules:** Scene changes, top motion events, and uniform sampling contribute candidates. The implementation caps selected frames at 120 and caps summary prompt input at 12,000 characters. Generated frame files are removed after execution.
- **Edge cases:** No frames extracted, failed frame write, unavailable VLM, long video, empty analysis response, corrupted source video.
- **Error handling:** Per-frame VLM failures become fallback frame descriptions; summary failures fall back to joined frame descriptions; media resources are always released.

## API Contract

| Operation | Input | Output | Description |
|---|---|---|---|
| `video-info` | `video` | Video metadata JSON | Read video properties |
| `extract-frames` | `video`, `interval` | JSON path list | Extract sampled frames |
| `convert` | `input_path`, `output_path` | Success JSON | Convert video format |
| `check-corruption` | `video` | Corruption JSON | Validate decodability |
| `create-gif` | `video`, `output_path`, optional `start`, `duration` | Success JSON | Create GIF segment |
| `detect-scenes` | `video`, `threshold` | Scene event list | Detect transitions |
| `detect-motion` | `video`, `min_area` | Motion event list | Detect motion |
| `track` | `video`, `bbox`, `max_frames` | Bounding-box list | Track an object |
| `timeline` | `video`, `interval` | Timeline JSON | Generate timeline |
| `analyze-video` | `video`, optional `prompt`, `interval`, `scene_threshold`, `min_area` | `VideoUnderstanding` JSON | Smart video understanding |

The feature uses these shared contracts:

- `contract_video_processing_protocol.py`
- `contract_video_analysis_protocol.py`
- `contract_video_timeline_protocol.py`
- `contract_object_tracking_protocol.py`
- `contract_video_understanding_protocol.py`
- `contract_ffmpeg_video_protocol.py`
- `contract_opencv_image_protocol.py`
- `contract_llm_vision_protocol.py`

## Integration Points

| Integration | Purpose |
|---|---|
| OpenCV | Frame capture, frame decoding, scene and motion processing |
| FFmpeg | Video metadata, conversion, corruption checks, and media operations |
| External VLM | Per-frame descriptions and summary synthesis for `analyze-video` |
| Root composition | Wires the image VLM adapter into video understanding |
| CLI | Exposes all video commands as `vision-arwaky-cli` subcommands |
| MCP | Exposes all video commands through `vision_execute` and discovery |

## Non-functional Requirements

- **Bounded work:** Smart-video analysis must not send an unbounded number of frames to the VLM.
- **Resource safety:** Capture handles must be released and temporary frame directories must be cleaned up.
- **Failure isolation:** Failure to analyze one frame must not discard all other frame results.
- **Determinism:** Core processing and analysis commands must work without a live VLM endpoint.
- **Maintainability:** The orchestrator must remain a pure delegation facade over injected contracts.
- **Observability:** External VLM and media adapter failures must include operation context in logs or returned errors.

## Test Scenarios / QA Checklist

- [ ] Read metadata from a generated valid MP4.
- [ ] Extract frames with a normal interval and an interval larger than the video.
- [ ] Convert a video and create a GIF segment with valid and invalid segments.
- [ ] Detect corruption for a valid, missing, and malformed file.
- [ ] Detect scenes and motion in static and changing videos.
- [ ] Track an object with a valid bounding box and handle an invalid bounding box.
- [ ] Generate a timeline for a video with no detected events.
- [ ] Run smart-video analysis with a fake VLM and verify structured output.
- [ ] Verify smart-video sampling never exceeds 120 frames.
- [ ] Verify per-frame VLM failure produces fallback descriptions.
- [ ] Verify generated frame paths do not exist after smart-video analysis returns.
- [ ] Verify `analyze-video` is present in both CLI parser and MCP discovery.
- [ ] Verify Python 3.12 and 3.13 CI test jobs pass.

## Assumptions and Constraints

Smart-video analysis requires a configured OpenAI-compatible VLM endpoint. The deterministic video commands remain usable without that endpoint. Long videos are intentionally summarized from a bounded representative sample rather than exhaustively analyzed.

## Glossary

- **FPS:** Frames per second.
- **VLM:** Vision-language model.
- **Key frame:** A selected frame representative of a scene, motion event, or uniform sample.
- **Timeline:** A structured sequence of sampled video events.

## Reference

- [Product requirements](../../PRD.md)
- [Developer README](../../README.md)
- [Agent-facing skill](../../SKILL.md)
