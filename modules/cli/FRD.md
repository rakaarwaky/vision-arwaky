# FRD — Command-Line Interface

## System Overview

The CLI is the developer-facing command surface for Vision Arwaky. It parses arguments into command-specific namespaces, builds the application graph, injects the root dispatcher, calls a command handler, and prints the returned value. Command handlers do not compose feature implementations; all execution is routed through the aggregate facade.

```text
vision-arwaky-cli
        │
        ▼
argparse controller
        │
        ▼
command handler surface
        │
        ▼
RootDispatcher
        │
        ▼
Image / Video feature graph
```

Primary implementation files are `surface_cli_controller.py`, `surface_cli_command.py`, and `root_cli_entry.py`.

## Functional Requirements

### FR-CLI-001: Parse commands

- **Description:** Expose a stable parser for image, video, and smart-video commands.
- **Input:** Command-line arguments.
- **Output:** Parsed command namespace.
- **Business rules:** Required paths must be declared as required arguments; optional values must have documented defaults.
- **Edge cases:** No command, unknown command, missing required argument, malformed numeric value.
- **Error handling:** Argparse must print usage and return a non-zero process status for invalid invocations.

### FR-CLI-002: Execute image commands

- **Description:** Route `analyze`, `ocr`, and `compare` to the root dispatcher.
- **Input:** Image paths, optional prompt, and OCR language.
- **Output:** Printed command result.
- **Business rules:** The handler passes validated values and does not instantiate image capabilities.
- **Edge cases:** Missing files, unavailable VLM, unavailable Tesseract, invalid comparison pair.
- **Error handling:** Preserve the dispatcher’s controlled error behavior and return a non-zero status where appropriate.

### FR-CLI-003: Execute video commands

- **Description:** Route deterministic video operations (`video-info`, `extract-frames`, `check-corruption`, `detect-scenes`, `detect-motion`, `track`) and `analyze-video` to the video orchestrator through the root dispatcher.
- **Input:** Video path and command-specific parameters such as bounding box.
- **Output:** Printed JSON or structured command output.
- **Business rules:** `analyze-video` accepts a prompt and video path. Frame sampling bounds and parameters are managed predictably.
- **Edge cases:** Missing media, invalid numeric values, unavailable FFmpeg/OpenCV, unreachable VLM, invalid bounding boxes.
- **Error handling:** Return a controlled command error and preserve the process status contract.

## API Contract

| Entry point | Arguments | Output |
|---|---|---|
| `vision-arwaky-cli analyze` | `--image`, optional `--prompt` | Image analysis output |
| `vision-arwaky-cli ocr` | `--image`, optional `--lang` | OCR output |
| `vision-arwaky-cli compare` | `--image1`, `--image2` | Comparison output |
| `vision-arwaky-cli video-info` | `--video` | Video metadata |
| `vision-arwaky-cli extract-frames` | `--video` | Extracted frame paths |
| `vision-arwaky-cli check-corruption` | `--video` | Video decodability result |
| `vision-arwaky-cli detect-scenes` | `--video` | Scene transitions |
| `vision-arwaky-cli detect-motion` | `--video` | Motion events |
| `vision-arwaky-cli track` | `--video`, `--bbox` | Tracked bounding boxes |
| `vision-arwaky-cli analyze-video` | `--video`, optional `--prompt` | Smart-video JSON summary |


The complete command table is maintained in the root [README.md](../../README.md).

## Integration Points

The CLI integrates with `root_composition_container.build`, `RootDispatcher`, and all feature orchestrators. It is packaged as `vision-arwaky-cli` through the `project.scripts` configuration in `pyproject.toml`.

## Non-functional Requirements

- **Usability:** `--help` must describe every command and its required arguments.
- **Safety:** User-provided input must remain data passed to Python APIs, not shell-evaluated command strings.
- **Testability:** Parser registration, handler routing, and entry-point imports must be testable without a live VLM.
- **Compatibility:** The CLI must run on Python 3.12 and 3.13.
- **Output stability:** Command handlers should print dispatcher output without introducing inconsistent ad-hoc schemas.

## Test Scenarios / QA Checklist

- [ ] `vision-arwaky-cli --help` lists every command.
- [ ] `vision-arwaky-cli analyze-video --help` lists its sampling options.
- [ ] Image parser tests cover all four image commands.
- [ ] Video parser tests cover all deterministic commands and `analyze-video`.
- [ ] Missing required arguments return a parser error.
- [ ] The test command reports missing pytest cleanly.
- [ ] Temporary middle-frame files are deleted after image analysis.
- [ ] CLI entry module imports without building an external model.
- [ ] `bash scripts/gates.sh` passes.

## Assumptions and Constraints

The CLI assumes that project dependencies are installed through `uv sync` and that system dependencies are available for the selected command. VLM-backed commands require a configured external endpoint, while deterministic commands do not.

## Reference

- [Product requirements](../../PRD.md)
- [MCP FRD](../mcp/FRD.md)
- [Developer README](../../README.md)
- [Agent-facing skill](../../SKILL.md)
