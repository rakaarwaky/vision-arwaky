# FRD — Command-Line Interface

## Feature Overview

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

**Description:** Expose a stable argparse parser that turns command-line arguments into a command-specific namespace for workspace, image, video, and smart-video commands.

#### Business Logic

- Required paths are declared as required arguments; optional values carry documented defaults.
- The parser covers every public command exactly once.
- Unknown flags and bloat commands (`elements`, `convert`, `create-gif`, `timeline`, `test`) are excluded from the public surface.

#### Edge Cases

- No command, unknown command, missing required argument, malformed numeric value (e.g. invalid `--bbox`).

#### Technical Specification

| Aspect | Detail |
|--------|--------|
| **Input** | Command-line arguments (`sys.argv`). Source: the terminal invocation of `vision-arwaky-cli` / `va`. |
| **Output** | Parsed `argparse.Namespace` with a `command` attribute and command-specific fields. Destination: the CLI command handler surface. |
| **Protocol** | `IRegistryServiceAggregate` |
| **Method** | `execute_in_process` |
| **Event** | None |
| **Error** | Prints usage and returns a non-zero process status for invalid invocations. |

#### Test

| Context | When Action | Then Observable Result |
|---------|-------------|------------------------|
| No arguments supplied | `create_parser().parse_args([])` | Prints usage and returns non-zero status |
| Unknown command supplied | `parse_args(["bogus"])` | Prints usage and returns non-zero status |
| `init` with no target dir | `parse_args(["init"])` | `args.target_dir` defaults to `.` |

#### Metric

| Target Metric | Value |
|---------------|-------|
| Public Commands Registered | 11 |
| Excluded Bloat Commands | 0 |
| Invalid Invocation Exit Status | Non-zero |

### FR-CLI-002: Execute workspace commands

**Description:** Route `init` to the workspace provisioner through the system orchestrator.

#### Business Logic

- Creates `.agents/skills/vision-arwaky/SKILL.md` from the embedded constant.
- Provisions the `.vision-arwaky` symlinks pointing at XDG directories.
- Symlinks `.venv` when an XDG virtualenv exists.
- Adds entries to `.git/info/exclude` with a local ignore file as fallback.
- Creation is idempotent; invalid symlinks are replaced.

#### Edge Cases

- Missing `.git` directory, non-existent target path, existing symlinks or files, absent isolated virtualenv.

#### Technical Specification

| Aspect | Detail |
|--------|--------|
| **Input** | Optional target directory (default `.`). Source: CLI `init` command via `cmd_init`. |
| **Output** | JSON summary of created XDG paths, symlinks, the SKILL.md file, and exclusion status. Destination: stdout / caller. |
| **Protocol** | `IWorkspaceProtocol` |
| **Method** | `init_workspace` |
| **Event** | None |
| **Error** | Structured status returned for every path that could not be written; invalid symlinks replaced. |

#### Test

| Context | When Action | Then Observable Result |
|---------|-------------|------------------------|
| Empty target directory | `init` invoked | Reports created XDG paths, symlinks, SKILL.md, exclusion status |
| Running init twice | `init` invoked again | Valid symlinks remain in place (idempotent) |
| Missing `.git` directory | `init` invoked | Local ignore file used as fallback; structured status returned |

#### Metric

| Target Metric | Value |
|---------------|-------|
| Init Command Exit Status | 0 on success |
| Idempotent Re-runs | 100% valid symlinks |

### FR-CLI-003: Execute image commands

**Description:** Route `analyze`, `ocr`, and `compare` to the image orchestrator; a video passed to `analyze` has its middle frame extracted first.

#### Business Logic

- The handler passes validated values and never instantiates image capabilities directly.
- The default OCR language is `eng`.
- Video input to `analyze` triggers middle-frame extraction before analysis.

#### Edge Cases

- Missing files, unavailable VLM, unavailable Tesseract, invalid comparison pair, video input to `analyze`.

#### Technical Specification

| Aspect | Detail |
|--------|--------|
| **Input** | Image paths, optional prompt, and OCR language (`--image`, `--prompt`, `--lang`). Source: CLI image commands. |
| **Output** | Printed command result (analysis text, OCR text, or comparison report). Destination: stdout / caller. |
| **Protocol** | `IImageProcessingProtocol` |
| **Method** | `analyze_screenshot`, `extract_text`, `compare_screenshots` |
| **Event** | None |
| **Error** | Controlled error behaviour preserved; non-zero status returned where appropriate (e.g. missing file, unavailable VLM/Tesseract). |

#### Test

| Context | When Action | Then Observable Result |
|---------|-------------|------------------------|
| Valid image, reachable VLM | `analyze` invoked | Structured analysis output printed |
| Image without `--lang` | `ocr` invoked | OCR text returned using default language `eng` |
| Video passed to `analyze` | `analyze` invoked | Middle frame extracted and analyzed |
| Missing image file | `ocr` invoked | Controlled error, non-zero status |

#### Metric

| Target Metric | Value |
|---------------|-------|
| Default OCR Language | `eng` |
| OCR Fallback on Endpoint Failure | 100% |

### FR-CLI-004: Execute video commands

**Description:** Route deterministic video operations (`video-info`, `extract-frames`, `check-corruption`, `detect-scenes`, `detect-motion`, `track`) and `analyze-video` to the video orchestrator.

#### Business Logic

- `analyze-video` accepts a prompt and a video path.
- Frame sampling bounds and parameters are managed predictably inside the domain.
- No tuning parameters are exposed publicly.

#### Edge Cases

- Missing media, invalid numeric values, unavailable FFmpeg or OpenCV, unreachable VLM, invalid bounding boxes.

#### Technical Specification

| Aspect | Detail |
|--------|--------|
| **Input** | Video path and command-specific parameters (e.g. `--bbox` for `track`, `--prompt` for `analyze-video`). Source: CLI video commands. |
| **Output** | Printed JSON or structured command output. Destination: stdout / caller. |
| **Protocol** | `IVideoProcessingProtocol`, `IVideoAnalysisProtocol`, `IObjectTrackingProtocol`, `ILLMVisionProtocol` |
| **Method** | `get_info`, `extract_frames`, `check_corruption`, `detect_scenes`, `detect_motion`, `track_object`, `analyze_image` |
| **Event** | None |
| **Error** | Controlled command error returned; process status contract preserved. |

#### Test

| Context | When Action | Then Observable Result |
|---------|-------------|------------------------|
| Valid video | `video-info` invoked | Video metadata output printed |
| Valid video with `--bbox` | `track` invoked | Bounding-box trajectory list printed |
| Missing media file | any video command invoked | Controlled error, non-zero status |
| Invalid `--bbox` format | `track` invoked | Error message printed, non-zero status |

#### Metric

| Target Metric | Value |
|---------------|-------|
| Video Command Invalid-Input Exit Status | Non-zero |
| Tuning Flags in Public Video Set | 0 |

### FR-CLI-005: Keep tuning parameters out of the public surface

**Description:** The public command surface deliberately exposes no tuning parameters such as frame interval, scene threshold, motion minimum area, or tracking frame budget.

#### Business Logic

- Tuning values are controlled by shared constants (`FRAME_EXTRACTION_INTERVAL_S`, `SCENE_THRESHOLD`, `MIN_MOTION_AREA`, `MAX_TRACK_FRAMES`).
- Orchestrators may accept tuning arguments for internal use, but those arguments are outside the public command contract.

#### Edge Cases

- A caller passes an unknown tuning flag; a caller expects a threshold flag on a detection command.

#### Technical Specification

| Aspect | Detail |
|--------|--------|
| **Input** | Only stable user-facing inputs: paths, prompt, language, and bounding box where required. Source: CLI command surface. |
| **Output** | Deterministic command behaviour with no tunable surface to guess at. Destination: stdout / caller. |
| **Protocol** | `IRegistryServiceAggregate` |
| **Method** | `execute_in_process` |
| **Event** | None |
| **Error** | Unknown arguments rejected by the parser with usage output and a non-zero process status. |

#### Test

| Context | When Action | Then Observable Result |
|---------|-------------|------------------------|
| Unknown tuning flag passed | parser invoked | Usage output printed, non-zero status |
| Detection command run | `detect-scenes` invoked | Runs with fixed threshold from shared constant |

#### Metric

| Target Metric | Value |
|---------------|-------|
| Tuning Flags in Public Command Set | 0 |
| Unknown Flag Rejection Exit Status | Non-zero |

## Public Interface

| Aspect | Detail |
|--------|--------|
| Agent | `CommandHandlerSurface` (CLI command surface) |
| Aggregate | `IRegistryServiceAggregate` |
| Method | `execute_in_process` |
| Request | `CommandName` + kwargs dict |
| Response | `CommandOutput` |

## Reference

| Artifact | Purpose | Link |
|----------|---------|------|
| PRD | Business goals, user stories, and scope | [PRD.md](../../PRD.md) |
| Backlog | Task tracking, epics, and implementation status | [BACKLOG.md](BACKLOG.md) |
| Roadmap | Timeline, phasing, and dependencies | [ROADMAP.md](../../ROADMAP.md) |
| Architecture | System boundaries, tech stack, and infrastructure | [ARCHITECTURE.md](../../ARCHITECTURE.md) |
