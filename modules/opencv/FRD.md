# FRD — OpenCV Infrastructure

## System Overview

The OpenCV module is the shared infrastructure adapter used by image and video features. It provides a contract-backed access point to OpenCV operations and video capture. Feature orchestrators receive the adapter through constructor injection; they do not import OpenCV directly for composition.

```text
Image / Video capabilities
          │
          ▼
OpenCVImageProtocol
          │
          ▼
OpenCVImageAdapter
          │
          ▼
OpenCV runtime
```

The module is intentionally small. Its primary implementation files are `capabilities_opencv_image_adapter.py` and `root_opencv_container.py`.

## Functional Requirements

### FR-OCV-001: Build the OpenCV adapter

- **Description:** Construct one reusable OpenCV adapter for the application graph.
- **Input:** No user input; the root container creates the adapter.
- **Output:** An implementation of `OpenCVImageProtocol`.
- **Business rules:** The adapter must be injected into image and video feature containers.
- **Edge cases:** OpenCV import failure or unavailable codec support.
- **Error handling:** Surface a controlled dependency error during status or feature execution.

### FR-OCV-002: Read and write images

- **Description:** Provide image decoding, encoding, and basic image operations required by image capabilities.
- **Input:** Valid file paths and image data.
- **Output:** OpenCV image objects or persisted image files.
- **Business rules:** The adapter must not silently report a failed write as successful.
- **Edge cases:** Missing file, unsupported extension, permissions, empty image.
- **Error handling:** Return a controlled error or false result that the calling capability can interpret.

### FR-OCV-003: Open video capture

- **Description:** Open a video source for frame-based processing.
- **Input:** A validated video path.
- **Output:** A capture object exposing frame position, read, and release operations.
- **Business rules:** Consumers must release the capture object in a `finally` block.
- **Edge cases:** Missing file, unsupported codec, empty stream, read failure.
- **Error handling:** The adapter or calling capability must produce a diagnostic media error.

### FR-OCV-004: Expose runtime compatibility

- **Description:** Provide the OpenCV module object and adapter methods needed by the video and image ports without leaking dependency construction into surfaces.
- **Input:** Internal feature requests.
- **Output:** Contract-compatible operations.
- **Business rules:** Surfaces such as CLI and MCP must use the root graph rather than instantiate this adapter directly.
- **Edge cases:** Headless environment, missing GUI capabilities, codec differences across platforms.
- **Error handling:** Status and feature commands must distinguish OpenCV import failure from invalid media input.

## API Contract

| Operation | Input | Output | Description |
|---|---|---|---|
| `build_opencv` | None | `OpenCVImageAdapter` | Create the shared adapter |
| Adapter image methods | Image paths or arrays | Images or result values | Support image capabilities |
| `get_video_capture` | `path` | Capture object | Open a video stream |
| `cv2` property | None | OpenCV module | Allow capabilities to use the injected runtime |

## Integration Points

OpenCV is injected into the image root, video root, CLI helper paths, and the global composition graph. FFmpeg remains the source of truth for operations that require media probing or conversion; OpenCV is used for frame access and image-level processing.

## Non-functional Requirements

- **Portability:** The adapter must run in the headless CI environment.
- **Resource safety:** Video capture consumers must release handles even when frame reads fail.
- **Testability:** Feature tests must be able to inject a fake or controlled adapter.
- **Maintainability:** OpenCV-specific details remain behind the shared contract where possible.

## Test Scenarios / QA Checklist

- [ ] Import the adapter in a headless environment.
- [ ] Open a generated valid video and read a frame.
- [ ] Release a capture after successful and failed reads.
- [ ] Read and write a valid image.
- [ ] Handle a missing image path without an unhandled native exception.
- [ ] Verify image and video root containers receive the same shared OpenCV adapter.
- [ ] Run the full Python 3.12 and 3.13 test matrix.

## Assumptions and Constraints

OpenCV is a runtime dependency installed through the headless distribution. GUI-specific functionality is not part of the product contract.

## Reference

- [Product requirements](../../PRD.md)
- [Image FRD](../image/FRD.md)
- [Video FRD](../video/FRD.md)
- [Developer README](../../README.md)
