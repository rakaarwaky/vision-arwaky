# FRD — Command-Line Interface

## System Overview

The CLI is the developer-facing command surface for Vision Arwaky (available via `vision-arwaky-cli` and the short alias `va`). It parses arguments into command-specific namespaces, determines the target domain via `CommandDomain.from_command()`, instantiates the corresponding domain container, and invokes the command handler with the container's orchestrator.

```text
vision-arwaky-cli / va
        │
        ▼
argparse controller (`surface_cli_controller.py`)
        │
        ▼
command handler surface (`surface_cli_command.py`)
        │
        ▼
_resolve_orchestrator (`root_cli_entry.py`)
  ├── ImageContainer  → ImageOrchestrator
  ├── VideoContainer  → VideoOrchestrator
  └── SystemContainer → SystemOrchestrator
```

Primary implementation files are `modules/cli/src/surface_cli_controller.py`, `modules/cli/src/surface_cli_command.py`, `modules/cli/src/surface_tui_component.py`, `modules/root_cli_entry.py`, and `modules/root_tui_entry.py`.

## Functional Requirements

### FR-CLI-001: Parse commands

- **Description:** Expose a stable parser for workspace, image, video, and smart-video commands.
- **Input:** Command-line arguments.
- **Output:** Parsed command namespace.
- **Business rules:** Required paths must be declared as required arguments; optional values must have documented defaults.
- **Edge cases:** No command, unknown command, missing required argument, malformed numeric value.
- **Error handling:** Argparse must print usage and return a non-zero process status for invalid invocations.

### FR-CLI-002: Execute workspace commands

- **Description:** Route `init` to the workspace provisioner through the system orchestrator.
- **Input:** Optional `target_dir` (default: `.`).
- **Output:** JSON summary of created XDG paths, symlinks, skill guide file, and git exclusion status.
- **Business rules:** Creates `.agents/skills/vision-arwaky/SKILL.md` from the embedded constant, provisions `.vision-arwaky` symlinks pointing to XDG directories, symlinks `.venv` if an XDG virtualenv exists, and adds entries to `.git/info/exclude` (or fallback `.gitignore`).
- **Edge cases:** Missing `.git` directory, non-existent target path, existing symlinks/files.
- **Error handling:** Safe idempotent creation, overwriting invalid symlinks, and returning structured status.

### FR-CLI-003: Execute image commands

- **Description:** Route `analyze`, `ocr`, and `compare` to the image orchestrator. Video files passed to `analyze` have their middle frame extracted via `utility_frame_extractor`.
- **Input:** Image paths, optional prompt, and OCR language.
- **Output:** Printed command result.
- **Business rules:** The handler passes validated values and does not instantiate image capabilities directly.
- **Edge cases:** Missing files, unavailable VLM, unavailable Tesseract, invalid comparison pair.
- **Error handling:** Preserve controlled error behavior and return a non-zero status where appropriate.

### FR-CLI-004: Execute video commands

- **Description:** Route deterministic video operations (`video-info`, `extract-frames`, `check-corruption`, `detect-scenes`, `detect-motion`, `track`) and `analyze-video` to the video orchestrator.
- **Input:** Video path and command-specific parameters such as bounding box.
- **Output:** Printed JSON or structured command output.
- **Business rules:** `analyze-video` accepts a prompt and video path. Frame sampling bounds and parameters are managed predictably.
- **Edge cases:** Missing media, invalid numeric values, unavailable FFmpeg/OpenCV, unreachable VLM, invalid bounding boxes.
- **Error handling:** Return a controlled command error and preserve the process status contract.

## API Contract

| Entry point | Arguments | Output |
|---|---|---|
| `vision-arwaky-cli init` / `va init` | `[target_dir]` (optional, default: `.`) | JSON report of created workspace files and symlinks |
| `vision-arwaky-cli analyze` / `va analyze` | `--image`, optional `--prompt` | Image analysis output |
| `vision-arwaky-cli ocr` / `va ocr` | `--image`, optional `--lang` | OCR output |
| `vision-arwaky-cli compare` / `va compare` | `--image1`, `--image2` | Comparison output |
| `vision-arwaky-cli video-info` / `va video-info` | `--video` | Video metadata output |
| `vision-arwaky-cli extract-frames` / `va extract-frames` | `--video`, optional `--interval` | Frame extraction output |
| `vision-arwaky-cli check-corruption` / `va check-corruption` | `--video` | Decodability check output |
| `vision-arwaky-cli detect-scenes` / `va detect-scenes` | `--video`, optional `--threshold` | Scene boundary list |
| `vision-arwaky-cli detect-motion` / `va detect-motion` | `--video`, optional `--min_area` | Motion event list |
| `vision-arwaky-cli track` / `va track` | `--video`, `--bbox`, optional `--max_frames` | Bounding-box trajectory list |
| `vision-arwaky-cli analyze-video` / `va analyze-video` | `--video`, optional `--prompt` | Smart-video summary |
