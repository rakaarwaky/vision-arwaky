# Plan: image — Architect

> **Scope note:** Review performed against the provided knowledge base (`image` module v2.0.7 + `shared` definitions, `ARCHITECTURE.md`, `PRD.md`, `modules/image/FRD.md`). `RULES_AES.md` and `.agents/skills/` were not included in the knowledge base, so `ARCHITECTURE.md` (7-layer spec) is used as the authoritative rule baseline. Video/CLI/MCP/system modules are out of this file set, so cross-feature usage of shared code is marked "verify" rather than "orphan".
>
> **Suggested save path:** `modules/image/REVIEW_ARCHITECT.md`

## Summary

The `image` feature is structurally sound: file naming follows `layer_concern_role.py`, the orchestrator depends only on contracts, capabilities implement their protocols, the composition root wires concrete adapters via constructor injection, and the import graph is acyclic and unidirectional. However, there is **one critical taxonomy-layer breach** (`XDGPaths.ensure_dirs()` performs filesystem infrastructure inside a taxonomy VO file), a **FRD-violating bypass of the OpenCV utility layer** in `ImageProcessingProcessor`, dead code (`DEFAULT_LLM_URL`, unused injected ports), and several scalability concerns (network I/O inside a property, a monolithic constants file embedding a ~200-line markdown blob, and a non-deterministic pHash fallback).

## Findings

### Layer Boundaries

| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| B1 | 🔴 CRITICAL | Taxonomy contains infrastructure behavior: `XDGPaths.ensure_dirs()` calls `mkdir(parents=True)`, and the class reads `os.environ` via static methods. ARCHITECTURE §5: *"Taxonomy must not contain business rules, infrastructure, or imports from other layers."* | `modules/shared/src/taxonomy_xdg_paths_vo.py` | Keep taxonomy as pure path definitions/constants. Move `ensure_dirs()` (and any env resolution logic) to a stateless utility, e.g. `utility_xdg_paths.py`, or into the `system` feature capability. |
| B2 | 🟡 WARNING | Capability bypasses the utility layer: `capabilities_image_processing_processor.py` calls `cv2.resize`, `cv2.copyMakeBorder`, `cv2.threshold` directly, while `utility_opencv_ops.py` already provides `resize_image`, `pad_image_border`, `apply_threshold`. FRD explicitly states: *"OpenCV operations are utilized directly via pure utility functions."* | `modules/image/src/capabilities_image_processing_processor.py` | Replace direct `cv2.*` calls with existing utility functions and remove `import cv2` from the capability. |
| B3 | 🟡 WARNING | DRY violation: `DEFAULT_LLM_URL = "http://127.0.0.1:1234/v1"` is duplicated in two utility files. | `modules/shared/src/utility_config_handler.py`, `modules/shared/src/utility_llm_check.py` | Define once — preferably as a taxonomy constant (compile-time literal) in `taxonomy_vision_constant.py` — and import in both utilities. |
| B4 | 🟢 INFO | Lazy `import pytesseract` / `from PIL import Image` inside `extract_text`. Acceptable external-adaptation pattern for optional system deps, and it powers the FRD-mandated actionable error. No change required. | `modules/image/src/capabilities_tesseract_ocr_adapter.py` | Keep as-is. |

### Naming

| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| N1 | 🟡 WARNING | Role mismatch: file is suffixed `_vo` (immutable data concept) but `XDGPaths` is a static-method provider with behavior — not a value object. | `modules/shared/src/taxonomy_xdg_paths_vo.py` | After extracting behavior (B1), either expose paths as constants/frozen VO data, or rename to reflect its real role. |
| N2 | 🟡 WARNING | Contract method lacks a return annotation, weakening the stable interface contract: `def extract_text(self, image_path, language):` | `modules/shared/src/contract_tesseract_ocr_protocol.py` | Add `-> str` to match sibling protocols (`OcrText` wrapping happens in the processor; the adapter returns `str`). |
| N3 | 🟢 INFO | Legacy logger names from a previous layout: `"mcp_server.infrastructure.llm"`, `"mcp_server.infrastructure.tesseract"`, `"mcp_server.utility.opencv"` do not match the current `modules/` package paths. | `capabilities_llm_vision_adapter.py`, `capabilities_tesseract_ocr_adapter.py`, `utility_opencv_ops.py` | Align logger names with current module paths (e.g. `modules.image.src...`) for observability (PRD NFR). |
| N4 | 🟢 INFO | `LLMVisionProtocol.analyze_image` hardcodes `timeout: int = 120` instead of reusing `DEFAULT_VLM_TIMEOUT_S` from taxonomy (allowed dependency). | `modules/shared/src/contract_llm_vision_protocol.py` | Use the taxonomy constant to avoid drift. |
| N5 | 🟢 INFO | `RegistryServiceAggregate.execute_in_process` types `kwargs: dict` (unparameterized) while the orchestrator uses `dict[str, Any]`. | `modules/shared/src/contract_registry_service_aggregate.py` | Use `dict[str, Any]` consistently. |

### Orphan

| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| O1 | 🟡 WARNING | Dead code: `DEFAULT_LLM_URL` is defined but never referenced in this file (the function always receives `base_url`). | `modules/shared/src/utility_llm_check.py` | Remove it, or use it as the default for `base_url` after deduplication (B3). |
| O2 | 🟡 WARNING | Unused injected ports: `ImageOrchestrator` stores `self._tesseract` and `self._llm` but routes **every** command through `self._image_processing` only. The agent carries dependencies it never coordinates. | `modules/image/src/agent_image_orchestrator.py`, `root_image_container.py` | Remove `tesseract`/`llm` from the orchestrator constructor and container wiring, or document an explicit routing need. |
| O3 | 🟢 INFO | Several `utility_opencv_ops.py` functions have no caller inside this file set (`write_image`, `detect_edges`, `compare_histograms`, `apply_dilate`, `apply_gaussian_blur`, `compute_histogram_hsv`, `compute_moments`, video ops). They are presumably consumed by the `video` feature, which is not in this review set. | `modules/shared/src/utility_opencv_ops.py` | Verify usage from `video`/`system` features; prune only if confirmed unused workspace-wide. |
| O4 | 🟢 INFO | `modules/image/src/__init__.py` exports the orchestrator and capabilities but not `ImageContainer` / `build_image_feature`, making the composition root less discoverable. | `modules/image/src/__init__.py` | Export root-container symbols for a consistent public API (surfaces must still consume the aggregate, not capabilities). |

### Scalability

| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| S1 | 🟡 WARNING | `LLMVisionAdapter.model` property performs network I/O (health check + `GET /models`) **and mutates** `self._model`. It is invoked on every `analyze` request via `_analyze_via_http` → `self.model.value`, so an unconfigured model triggers up to two HTTP round-trips per analysis. Properties should be side-effect-free. | `modules/image/src/capabilities_llm_vision_adapter.py` | Resolve the model once explicitly (e.g. `resolve_model()` called lazily and cached in `self._resolved_model`); keep the property as a pure accessor. |
| S2 | 🟡 WARNING | `taxonomy_vision_constant.py` is a god-file mixing frame extraction, scene/motion detection, tracking, image comparison, VLM defaults, **and a ~200-line `EMBEDDED_SKILL_MD` documentation blob**. This harms SRP and readability of the domain foundation layer. | `modules/shared/src/taxonomy_vision_constant.py` | Split per domain (`taxonomy_image_constant.py`, `taxonomy_video_constant.py`, ...). Move `EMBEDDED_SKILL_MD` to the `system` feature or a packaged resource — bundled documentation is not domain language. |
| S3 | 🟡 WARNING | Non-deterministic fallback in `compute_phash`: `str(hash(image.tobytes()))` uses Python's per-process salted `hash()`, so the same image yields different hashes across runs/processes → false `phash_diff=true` in `compare` when `cv2.img_hash` is unavailable. Breaks the PRD "local and reproducible" goal. | `modules/shared/src/utility_opencv_ops.py` | Use a stable digest (e.g. `hashlib.md5/sha1` of the bytes) or the already-computed average-hash bitstring path. |
| S4 | 🟢 INFO | `VisionAnalysis.source` is a free-form `str` ("llm"/"opencv"); `FrameAnalysis.source` likewise. | `modules/shared/src/taxonomy_vision_vo.py` | Use `Literal["llm", "opencv"]` or a taxonomy constant/enum to make the contract self-documenting. |

### Data Flow

| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| D1 | 🟢 INFO | Import graph verified unidirectional and acyclic: Surface → `RegistryServiceAggregate` (orchestrator) → Protocols → Capabilities → Utility → Taxonomy. No capability imports another capability; the agent knows only contracts. | All files | None. |
| D2 | 🟡 WARNING | Request-time side-effect chain: `analyze` → `_analyze_via_http` → `self.model` → `check_llm_endpoint` (HTTP) → optional `GET /models` (HTTP) → then the actual `POST /chat/completions`. Hidden repeated I/O inside the happy path (flow view of S1). | `capabilities_llm_vision_adapter.py` | Same as S1: cache model resolution; keep the request path to a single intended HTTP call. |
| D3 | 🟢 INFO | Fallback flow matches FRD-IMG-001: LLM failure (RuntimeError/ValueError/OSError/ImportError) degrades to deterministic OCR with `source="opencv"` and captured `error`; unreadable compare inputs raise a controlled `ValueError` instead of silently returning `identical=true`. | `capabilities_image_processing_processor.py` | None. |

## Violations

1. **ARCHITECTURE §5 (Taxonomy):** `taxonomy_xdg_paths_vo.py` contains infrastructure (`ensure_dirs()` → `mkdir`) and env-driven behavior. 🔴
2. **`modules/image/FRD.md` System Overview:** *"OpenCV operations are utilized directly via pure utility functions"* — partially violated by direct `cv2.resize` / `cv2.copyMakeBorder` / `cv2.threshold` in `ImageProcessingProcessor`. 🟡
3. **ARCHITECTURE §9 (Agent, spirit):** orchestrator holds capability ports it never coordinates (unused `_tesseract`, `_llm`). 🟡
4. **ARCHITECTURE §7 (Utility DRY):** `DEFAULT_LLM_URL` duplicated across two utility files. 🟡

## Action Items

- [x] **P0** Extract `ensure_dirs()` from taxonomy into a stateless utility; leave `XDGPaths` pure (B1, N1).
- [x] **P1** Replace direct `cv2` calls in `ImageProcessingProcessor` with `resize_image` / `pad_image_border` / `apply_threshold`; drop `import cv2` (B2).
- [x] **P1** Remove unused `tesseract`/`llm` ports from `ImageOrchestrator` and update `root_image_container.py` wiring (O2).
- [x] **P1** Delete unused `DEFAULT_LLM_URL` from `utility_llm_check.py`; deduplicate the remaining definition (O1, B3).
- [x] **P1** Replace salted-`hash()` pHash fallback with a stable digest (S3).
- [x] **P2** Refactor `LLMVisionAdapter.model` into cached, explicit resolution; property becomes pure (S1, D2).
- [x] **P2** Add `-> str` to `TesseractOCRProtocol.extract_text`; use `DEFAULT_VLM_TIMEOUT_S` in `LLMVisionProtocol`; parameterize `kwargs: dict[str, Any]` (N2, N4, N5).
- [ ] **P3** Split `taxonomy_vision_constant.py` per domain; relocate `EMBEDDED_SKILL_MD` to `system`/resource (S2).
- [x] **P3** Align legacy `mcp_server.*` logger names with current module paths (N3).
