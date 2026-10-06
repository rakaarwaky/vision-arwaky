# FRD — Image Intelligence

## Reference

- PRD: [PRD.md](../../PRD.md)
- Backlog: [BACKLOG.md](BACKLOG.md)
- Developer README: [README.md](../../README.md)
- Agent skill: [SKILL.md](../../SKILL.md)

## System Overview

The image feature provides image analysis, OCR, and screenshot comparison to the CLI and MCP surfaces. Surfaces dispatch through the image aggregate, which delegates to the orchestrator; the orchestrator resolves ports injected by the root composition. Deterministic pixel operations are pure utility functions, while OCR and vision analysis call external engines behind adapters.

```text
CLI / MCP surface
        │
        ▼
Image aggregate (execute)
        │
        ▼
Image orchestrator
   ┌────┼─────────────┐
   ▼    ▼             ▼
Image  OCR adapter    Vision
processing           model adapter
   │
   ▼
OpenCV utilities (pure functions)
```

## Functional Requirements

### FR-IMG-001: Analyze image

- **Description**: Analyze a supplied image with the configured vision-language model and return structured text or a deterministic fallback result.
- **Input**: `image` path and optional `prompt`.
- **Output**: JSON containing the analysis source and the returned text or detected elements, wrapped in the command output envelope.
- **Business Rules**: The image path must pass through the dispatcher; the vision adapter must use the configured endpoint and model settings; deterministic operations must not require a network call.
- **Edge Cases**: Missing image, unsupported image format, empty model response, unreachable model endpoint, malformed model response.
- **Error Handling**: Return a controlled command error or the fallback result; never expose a raw network exception to the surface.

### FR-IMG-002: Extract text with OCR

- **Description**: Extract text from an image using Tesseract.
- **Input**: `image` path and optional language code, defaulting to `eng`.
- **Output**: Plain extracted text wrapped in the command output envelope.
- **Business Rules**: Tesseract is an external dependency and must be detected by the dependency probe before the command runs; the language code defaults to `eng` when absent.
- **Edge Cases**: Missing Tesseract binary, missing language data, unreadable image, empty text result.
- **Error Handling**: Raise a controlled runtime error carrying an actionable dependency message.

### FR-IMG-003: Compare screenshots

- **Description**: Compare two screenshots and identify perceptual differences.
- **Input**: `image1` and `image2` paths.
- **Output**: JSON with `identical`, `phash_diff`, and the list of difference bounding boxes.
- **Business Rules**: Both images must be readable before comparison; the result must be JSON-serializable; unreadable input must never read as identical.
- **Edge Cases**: Different dimensions, missing files, visually identical images, completely different images.
- **Error Handling**: Return a controlled file or image-processing error rather than silently treating unreadable input as identical.

## API Contract

### Protocol API

| Method | Input | Output | Error | Event | Description |
|---|---|---|---|---|---|
| `analyze` | `image`, optional `prompt` | `CommandOutput` containing analysis JSON | `CommandError` on invalid input or unhandled vision endpoint failure | — | Vision-language analysis with deterministic fallback |
| `ocr` | `image`, optional `lang` (default `eng`) | `CommandOutput` containing extracted text | `RuntimeError` naming the missing dependency | — | Tesseract text extraction |
| `compare` | `image1`, `image2` | `CommandOutput` containing comparison JSON | `CommandError` on unreadable input | — | Perceptual screenshot comparison |

### Aggregate API

| Method | Input | Output | Error | Event | Description |
|---|---|---|---|---|---|
| `execute` | command name (`analyze`, `ocr`, `compare`) plus that command's arguments | `CommandOutput` for the dispatched command | `CommandError` raised by the dispatched command | — | Single composite entry point the surfaces call |

## Integration Points

| System | Direction | Purpose | Failure mode |
|---|---|---|---|
| OpenCV utilities | in | Image decoding, processing, and perceptual comparison as pure functions | unreadable or unsupported input -> controlled image error |
| Tesseract engine | out | OCR execution through the OCR adapter | missing binary or language data -> actionable dependency error |
| External vision endpoint | out | Image understanding through an OpenAI-compatible chat completions endpoint | unreachable or malformed response -> deterministic fallback or controlled error |
| Root composition | in | Injects OCR and vision ports into the image orchestrator | missing port -> composition fails before any command runs |
| CLI and MCP surfaces | in | Public command entry points that call the aggregate | invalid arguments -> controlled command error |

## Non-functional Requirements

| Metric | Target | Measurement method |
|---|---|---|
| Determinism | Deterministic image operations make no network call | Run `compare` and `ocr` with the vision endpoint unreachable and assert the command completes |
| Reliability | Vision endpoint failures resolve to a fallback result or a controlled error | Exercise a simulated endpoint outage through the aggregate and assert the caller-visible outcome |
| Security | Image paths and endpoint configuration are never interpolated into shell commands | Architecture lint plus a path-injection test |
| Compatibility | Runs on Python 3.12+ with the OpenCV runtime installed by CI | CI matrix run across the supported interpreter versions |
| Maintainability | The orchestrator depends only on contracts and injected ports | Architecture scan reporting any dependency violation |

## Test Scenarios

- Analyze a valid image with a reachable local vision adapter and receive a structured analysis result.
- Analyze a valid image when the vision endpoint is unavailable and receive the deterministic fallback result.
- Run OCR with the default `eng` language and receive the extracted text.
- Run OCR with a missing Tesseract executable and receive the actionable dependency error.
- Compare identical screenshots and verify `identical=true`.
- Compare different screenshots and verify that differences are returned.
- Verify missing input files produce controlled errors.
- Verify the image root composition injects every required port.

## Assumptions & Constraints

- The repository does not bundle a vision model or model weights; the external backend is configured separately.
- Deterministic image operations remain the supported path when no vision endpoint is reachable.
- Tesseract and its language data are host-level dependencies installed outside this feature.
- The vision endpoint speaks an OpenAI-compatible chat completions protocol.

## Glossary

- **VLM**: Vision-language model used for image descriptions.
- **OCR**: Optical character recognition.
- **pHash**: Perceptual hash used to compare image similarity.
- **Port**: Contract interface consumed by an orchestrator or provided by a capability.
- **Aggregate**: Composite entry point the surfaces call to dispatch a command.
