# FRD — Image Intelligence

## Feature Overview

The image feature sits in the feature layer, invoked by the CLI and MCP surfaces through the image aggregate. It coordinates image analysis, OCR, and screenshot comparison capabilities, delegating to the vision-language adapter and Tesseract adapter behind contracts. Deterministic pixel operations are pure utility functions; OCR and vision analysis call external engines behind adapters.

## Functional Requirements

### FR-IMG-001: Analyze image

**Description:** Analyze a supplied image with the configured vision-language model and return structured text or a deterministic fallback result.

#### Business Logic

- The image path must pass through the dispatcher before any analysis runs.
- The vision adapter must use the configured endpoint and model settings.
- Deterministic operations must not require a network call.

#### Edge Cases

- Missing image, unsupported image format, empty model response, unreachable model endpoint, malformed model response.

#### Technical Specification

| Aspect | Detail |
|--------|--------|
| **Input** | `image` path and optional `prompt`. Source: caller command request. |
| **Output** | JSON containing the analysis source and the returned text or detected elements, wrapped in the command output envelope. Destination: caller. |
| **Protocol** | `ILLMVisionProtocol` |
| **Method** | `analyze` |
| **Event** | None |
| **Error** | Controlled command error or the deterministic fallback result; never a raw network exception. |

#### Test

| Context | When Action | Then Observable Result |
|---------|-------------|------------------------|
| Valid image with reachable vision adapter | `analyze` is invoked | Structured analysis result is returned |
| Valid image with unreachable vision endpoint | `analyze` is invoked | Deterministic fallback result is returned |
| Missing image path | `analyze` is invoked | Controlled command error is raised |

#### Metric

| Target Metric | Value |
|---------------|-------|
| Fallback Rate on Endpoint Failure | 100% |
| Raw Network Exceptions Exposed | 0 |

### FR-IMG-002: Extract text with OCR

**Description:** Extract text from an image using Tesseract.

#### Business Logic

- Tesseract is an external dependency and must be detected by the dependency probe before the command runs.
- The language code defaults to `eng` when absent.

#### Edge Cases

- Missing Tesseract binary, missing language data, unreadable image, empty text result.

#### Technical Specification

| Aspect | Detail |
|--------|--------|
| **Input** | `image` path and optional language code (default `eng`). Source: caller command request. |
| **Output** | Plain extracted text wrapped in the command output envelope. Destination: caller. |
| **Protocol** | `ITesseractOcrProtocol` |
| **Method** | `ocr` |
| **Event** | None |
| **Error** | Controlled runtime error carrying an actionable dependency message. |

#### Test

| Context | When Action | Then Observable Result |
|---------|-------------|------------------------|
| Image with default `eng` language | `ocr` is invoked | Extracted text is returned |
| Missing Tesseract executable | `ocr` is invoked | Actionable dependency error is raised |
| Unreadable image file | `ocr` is invoked | Controlled image error is raised |

#### Metric

| Target Metric | Value |
|---------------|-------|
| Default Language Applied | `eng` |
| Dependency Errors with Actionable Message | 100% |

### FR-IMG-003: Compare screenshots

**Description:** Compare two screenshots and identify perceptual differences.

#### Business Logic

- Both images must be readable before comparison.
- The result must be JSON-serializable.
- Unreadable input must never read as identical.

#### Edge Cases

- Different dimensions, missing files, visually identical images, completely different images.

#### Technical Specification

| Aspect | Detail |
|--------|--------|
| **Input** | `image1` and `image2` paths. Source: caller command request. |
| **Output** | JSON with `identical`, `phash_diff`, and the list of difference bounding boxes. Destination: caller. |
| **Protocol** | `IImageProcessingProtocol` |
| **Method** | `compare` |
| **Event** | None |
| **Error** | Controlled file or image-processing error; never silently treats unreadable input as identical. |

#### Test

| Context | When Action | Then Observable Result |
|---------|-------------|------------------------|
| Identical screenshots | `compare` is invoked | `identical=true` is returned |
| Different screenshots | `compare` is invoked | Difference bounding boxes are returned |
| Missing input file | `compare` is invoked | Controlled error is raised, not a silent identical result |

#### Metric

| Target Metric | Value |
|---------------|-------|
| Unreadable Input Read as Identical | 0 |
| Results JSON-Serializable | 100% |

## Public Interface

| Aspect | Detail |
|--------|--------|
| Agent | `ImageOrchestrator` |
| Aggregate | `IImageProcessingAggregate` |
| Method | `execute` |
| Request | `ImageRequest` (`Analyze`, `Ocr`, `Compare`) |
| Response | `CommandOutput` |

## Reference

| Artifact | Purpose | Link |
|----------|---------|------|
| PRD | Business goals, user stories, and scope | [PRD.md](../../PRD.md) |
| Backlog | Task tracking, epics, and implementation status | [BACKLOG.md](BACKLOG.md) |
| Roadmap | Timeline, phasing, and dependencies | [ROADMAP.md](../../ROADMAP.md) |
| Architecture | System boundaries, tech stack, and infrastructure | [ARCHITECTURE.md](../../ARCHITECTURE.md) |