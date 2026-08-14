# FRD — Image Intelligence

## System Overview

The image feature provides image analysis, OCR, UI-element detection, and screenshot comparison. Its root container assembles concrete adapters behind shared contracts and injects them into `ImageOrchestrator`. CLI and MCP surfaces call the aggregate facade rather than constructing image capabilities directly.

```text
CLI / MCP surface
        │
        ▼
RegistryServiceAggregate
        │
        ▼
ImageOrchestrator
   ┌────┼─────────────┐
   ▼    ▼             ▼
Image  Tesseract     LLM
processing           vision
   │    │             │
   └────┴──────┬──────┘
                ▼
          OpenCV adapter
```

Primary implementation modules are under `modules/image/src/`:

| Module | Responsibility |
|---|---|
| `agent_image_orchestrator.py` | Coordinates image commands through injected ports |
| `capabilities_image_processing_processor.py` | Implements image operations and fallback behavior |
| `capabilities_tesseract_ocr_adapter.py` | Adapts Tesseract OCR |
| `capabilities_llm_vision_adapter.py` | Calls an OpenAI-compatible external VLM endpoint |
| `root_image_container.py` | Builds the image dependency graph |

## Functional Requirements

### FR-IMG-001: Analyze image

- **Description:** Analyze a supplied image with the configured vision-language model and return structured text or a deterministic fallback result.
- **Input:** `image` path and optional `prompt`.
- **Output:** JSON containing the analysis source and returned text or detected elements.
- **Business rules:** The image path must be passed through the dispatcher and the VLM adapter must use configured endpoint and model settings.
- **Edge cases:** Missing image, unsupported image format, empty VLM response, unreachable VLM endpoint, malformed VLM response.
- **Error handling:** Return a controlled command error or fallback result; do not expose a raw unhandled network exception to the surface.

### FR-IMG-002: OCR

- **Description:** Extract text from an image using Tesseract.
- **Input:** `image` path and optional language code, defaulting to `eng`.
- **Output:** Plain extracted text serialized through the command output wrapper.
- **Business rules:** Tesseract is an external system dependency and must be detected by the status path.
- **Edge cases:** Missing Tesseract binary, missing language data, unreadable image, empty text.
- **Error handling:** Raise a controlled runtime error with an actionable dependency message.

### FR-IMG-003: Detect image elements

- **Description:** Detect visual or UI elements using the image-processing capability.
- **Input:** `image` path.
- **Output:** Structured element records with labels and bounding boxes.
- **Business rules:** Bounding boxes must use the shared taxonomy models rather than unvalidated dictionaries at contract boundaries.
- **Edge cases:** Empty image, no detected elements, unsupported dimensions, corrupt file.
- **Error handling:** Return an empty result for a valid image with no detections and a controlled error for invalid input.

### FR-IMG-004: Compare screenshots

- **Description:** Compare two screenshots and identify perceptual differences.
- **Input:** `image1` and `image2` paths.
- **Output:** `identical`, `phash_diff`, and a list of difference bounding boxes.
- **Business rules:** Both images must be readable before comparison; output must be JSON-serializable.
- **Edge cases:** Different dimensions, missing files, visually identical images, completely different images.
- **Error handling:** Return a controlled file or image-processing error rather than silently treating unreadable input as identical.

## API Contract

| Operation | Input | Output | Description |
|---|---|---|---|
| `analyze` | `image`, optional `prompt` | `CommandOutput` containing JSON | VLM analysis with fallback |
| `ocr` | `image`, optional `lang` | `CommandOutput` containing text | Tesseract OCR |
| `elements` | `image` | `CommandOutput` containing element JSON | UI or visual element detection |
| `compare` | `image1`, `image2` | `CommandOutput` containing comparison JSON | Screenshot comparison |

The feature uses the following shared contracts:

- `contract_image_processing_protocol.py`
- `contract_tesseract_ocr_protocol.py`
- `contract_llm_vision_protocol.py`
- `contract_opencv_image_protocol.py`

## Integration Points

| Integration | Purpose |
|---|---|
| OpenCV | Image decoding, processing, and perceptual comparison |
| Tesseract | OCR execution through the Tesseract adapter |
| External VLM | OpenAI-compatible `/chat/completions` endpoint for image understanding |
| Root composition | Injects OpenCV, OCR, and VLM capabilities into the image orchestrator |
| CLI and MCP | Public command surfaces |

## Non-functional Requirements

- **Performance:** Deterministic operations must not require a network call.
- **Reliability:** VLM failures must be handled through a fallback or explicit controlled error.
- **Security:** Image paths and endpoint configuration must not be interpolated into shell commands.
- **Compatibility:** The feature must work with Python 3.12 and 3.13 and the OpenCV runtime installed by CI.
- **Maintainability:** The orchestrator must depend on contracts and constructor-injected ports.

## Test Scenarios / QA Checklist

- [ ] Analyze a valid image with a reachable fake or local VLM adapter.
- [ ] Analyze a valid image when the VLM endpoint is unavailable and verify fallback behavior.
- [ ] Run OCR with the default `eng` language.
- [ ] Run OCR with a missing Tesseract executable and verify the diagnostic error.
- [ ] Detect elements in an image with and without detectable UI elements.
- [ ] Compare identical screenshots and verify `identical=true`.
- [ ] Compare different screenshots and verify differences are returned.
- [ ] Verify missing input files produce controlled errors.
- [ ] Verify the image root container injects every required port.

## Assumptions and Constraints

The repository does not bundle a VLM or model weights. The external backend must be configured separately, and deterministic image operations remain the supported fallback path when no VLM is available.

## Glossary

- **VLM:** Vision-language model used for image descriptions.
- **OCR:** Optical character recognition.
- **pHash:** Perceptual hash used to compare image similarity.
- **Port:** Contract interface consumed by an orchestrator or implemented by a capability.

## Reference

- [Product requirements](../../PRD.md)
- [Developer README](../../README.md)
- [Agent-facing skill](../../SKILL.md)
