# FRD — Command-Line Interface

## Reference

- Product requirements: [PRD.md](../../PRD.md)
- Feature backlog: [BACKLOG.md](BACKLOG.md)

## System Overview

The CLI is the developer-facing command surface for Vision Arwaky, available as `vision-arwaky-cli` and the short alias `va`. It parses arguments into command-specific namespaces, determines the target domain with the shared command-domain classifier, instantiates the matching domain container, and invokes the command handler with that container's orchestrator.

```text
vision-arwaky-cli / va
        │
        ▼
Argument controller
        │
        ▼
Command handler surface
        │
        ▼
Root orchestrator resolver
  ├── Image  -> Image Orchestrator
  ├── Video  -> Video Orchestrator
  └── System -> System Orchestrator
```

## Functional Requirements

### FR-CLI-001: Parse commands

- **Description**: Expose a stable parser for workspace, image, video, and smart-video commands.
- **Input**: Command-line arguments.
- **Output**: Parsed command namespace.
- **Business Rules**: Required paths are declared as required arguments; optional values carry documented defaults; the parser covers every public command exactly once.
- **Edge Cases**: No command, unknown command, missing required argument, malformed numeric value.
- **Error Handling**: The parser prints usage and returns a non-zero process status for invalid invocations.

### FR-CLI-002: Execute workspace commands

- **Description**: Route `init` to the workspace provisioner through the system orchestrator.
- **Input**: Optional target directory, defaulting to the current directory.
- **Output**: JSON summary of created XDG paths, symlinks, the skill guide file, and exclusion status.
- **Business Rules**: Creates `.agents/skills/vision-arwaky/SKILL.md` from the embedded constant, provisions the `.vision-arwaky` symlinks pointing at XDG directories, symlinks `.venv` when an XDG virtualenv exists, and adds entries to `.git/info/exclude` with a local ignore file as fallback.
- **Edge Cases**: Missing `.git` directory, non-existent target path, existing symlinks or files, absent isolated virtualenv.
- **Error Handling**: Creation is idempotent, invalid symlinks are replaced, and a structured status is returned for every path that could not be written.

### FR-CLI-003: Execute image commands

- **Description**: Route `analyze`, `ocr`, and `compare` to the image orchestrator; a video passed to `analyze` has its middle frame extracted first.
- **Input**: Image paths, optional prompt, and OCR language.
- **Output**: Printed command result.
- **Business Rules**: The handler passes validated values and never instantiates image capabilities directly; the default OCR language is `eng`.
- **Edge Cases**: Missing files, unavailable VLM, unavailable Tesseract, invalid comparison pair, video input to `analyze`.
- **Error Handling**: Controlled error behaviour is preserved and a non-zero status is returned where appropriate.

### FR-CLI-004: Execute video commands

- **Description**: Route deterministic video operations (`video-info`, `extract-frames`, `check-corruption`, `detect-scenes`, `detect-motion`, `track`) and `analyze-video` to the video orchestrator.
- **Input**: Video path and command-specific parameters such as a bounding box or prompt.
- **Output**: Printed JSON or structured command output.
- **Business Rules**: `analyze-video` accepts a prompt and a video path; frame sampling bounds and parameters are managed predictably inside the domain.
- **Edge Cases**: Missing media, invalid numeric values, unavailable FFmpeg or OpenCV, unreachable VLM, invalid bounding boxes.
- **Error Handling**: A controlled command error is returned and the process status contract is preserved.

### FR-CLI-005: Keep tuning parameters out of the public surface

- **Description**: The public command surface deliberately exposes no tuning parameters such as frame interval, scene threshold, motion minimum area, or tracking frame budget.
- **Input**: Only stable user-facing inputs: paths, prompt, language, and bounding box where required.
- **Output**: Deterministic command behaviour with no tunable surface to guess at.
- **Business Rules**: Tuning values are controlled by shared constants (`FRAME_EXTRACTION_INTERVAL_S`, `SCENE_THRESHOLD`, `MIN_MOTION_AREA`, `MAX_TRACK_FRAMES`); orchestrators may accept tuning arguments for internal use, but those arguments are outside the public command contract.
- **Edge Cases**: A caller passes an unknown tuning flag; a caller expects a threshold flag on a detection command.
- **Error Handling**: Unknown arguments are rejected by the parser with usage output and a non-zero process status.

## API Contract

### Protocol API

| Method | Input | Output | Error | Event | Description |
|--------|-------|--------|-------|-------|-------------|
| `init_workspace` | optional target directory (default `.`) | JSON report of created workspace paths and symlinks | workspace provisioning error | none | `vision-arwaky-cli init` / `va init`: workspace setup |
| `analyze_screenshot` | `--image`, optional `--prompt` | image analysis output | vision error | none | `vision-arwaky-cli analyze`: VLM analysis with deterministic fallback |
| `extract_text` | `--image`, optional `--lang` | OCR output | OCR error | none | `vision-arwaky-cli ocr`: text extraction, default language `eng` |
| `compare_screenshots` | `--image1`, `--image2` | comparison output | comparison error | none | `vision-arwaky-cli compare`: structural difference report |
| `get_info` | `--video` | video metadata output | video processing error | none | `vision-arwaky-cli video-info`: basic stream info |
| `extract_frames` | `--video` | frame extraction output | frame extraction error | none | `vision-arwaky-cli extract-frames`: interval fixed by a shared constant |
| `check_corruption` | `--video` | decodability check output | video processing error | none | `vision-arwaky-cli check-corruption`: decodability check |
| `detect_scenes` | `--video` | scene boundary list | analysis error | none | `vision-arwaky-cli detect-scenes`: threshold fixed by a shared constant |
| `detect_motion` | `--video` | motion event list | analysis error | none | `vision-arwaky-cli detect-motion`: minimum area fixed by a shared constant |
| `track_object` | `--video`, `--bbox` | bounding-box trajectory list | tracking error | none | `vision-arwaky-cli track`: frame budget fixed by a shared constant |
| `analyze` | `--video`, optional `--prompt` | smart-video summary | understanding error | none | `vision-arwaky-cli analyze-video`: bounded key frame VLM analysis |

### Aggregate API

| Method | Input | Output | Error | Event | Description |
|--------|-------|--------|-------|-------|-------------|
| `execute_in_process` | command name and keyword arguments | command output | command execution error | none | Single composite entry point the command handler calls to run a domain command |

## Integration Points

| System | Direction | Purpose | Failure mode |
|--------|-----------|---------|--------------|
| Domain orchestrators | out | Receive validated command arguments for image, video, and system work | orchestrator unavailable -> controlled command error |
| Shared command classifier | out | Decide which domain owns a command name | unknown command -> usage output and non-zero status |
| External LLM endpoint | out | Answer image and video analysis requests | unreachable -> deterministic fallback or controlled error |
| Media tooling (FFmpeg, Tesseract, OpenCV) | out | Decode video, extract frames, and read text | missing tool -> controlled error naming the tool |
| Workspace filesystem | out | Write the skill guide, symlinks, and exclusion entries | permission denied -> structured status for that path |

## Non-functional Requirements

| Metric | Target | Measurement method |
|--------|--------|--------------------|
| Invalid invocation exit status | non-zero for every rejected invocation | invocation matrix over malformed inputs |
| Startup to first result | under 1.5 s for a metadata command | timed cold run of `video-info` |
| Tunable surface | zero tuning flags in the public command set | parser introspection of every command |
| Output stability | same input yields byte-identical structured output | repeated run comparison |
| Error containment | every failure path returns a controlled status | fault injection across dependency failures |

## Test Scenarios

- Running the parser with no arguments prints usage and returns a non-zero process status.
- `init` on an empty directory reports created XDG paths, symlinks, the skill guide, and exclusion status, and running it twice leaves valid symlinks in place.
- `analyze` on a video file analyses the middle frame and returns the analysis output.
- `ocr` without `--lang` reads text with the default language.
- `detect-scenes` rejects an unknown flag and prints usage instead of running.
- A video command with missing media returns a controlled error and preserves the process status contract.

## Assumptions & Constraints

- The command names and their arguments are a stable contract; renaming one is a breaking change.
- Tuning values stay fixed by shared constants, so command behaviour stays bounded and predictable without guesswork from callers.
- The surface routes through orchestrators only; it never instantiates capabilities itself.
- The terminal UI surface shares the same orchestrator resolver and does not widen the command set.

## Glossary

- **Command**: One named invocation of the CLI, such as `init` or `detect-scenes`.
- **Domain**: The area a command belongs to — workspace, image, or video — decided by the shared classifier.
- **Orchestrator**: The domain coordinator the command handler receives from the root resolver.
- **Tuning parameter**: An internal control such as frame interval or scene threshold that the public surface deliberately withholds.
- **Process status**: The numeric code a command returns so callers can branch on success or failure.
