# Changelog

All notable changes to Vision Arwaky are documented in this file. The project follows a repository-level changelog rather than a strict release-automation format because package versioning and GitHub pull requests are currently managed separately.

## [Unreleased]

---

## [3.0.0] — 2026-08-30

### Added

- Added `TODO.md` with a feature matrix, acceptance checklist, evidence status, and explicit follow-up ownership for unresolved deployment and credential-history decisions.
- Added `tests/test_cli_e2e.py`, covering help behavior for all 15 CLI commands, deterministic image/video workflows, FFmpeg-backed commands, smart-video fallback, generated fixtures, and subprocess isolation through `stdin=subprocess.DEVNULL`.
- Added a dedicated `cli-e2e` GitHub Actions job with OpenCV, Tesseract, and FFmpeg system dependencies.
- Added `pytest-cov`, Ruff, and MyPy to the reproducible `dependency-groups.dev` configuration and refreshed `uv.lock`.
- Added a clean-wheel smoke test to the PyPI publish workflow. The built artifact is installed into a fresh virtual environment and the installed CLI help command is executed before publishing.

### Changed

- Added PEP 257 docstrings to public CLI handlers, parser construction, TUI screens, and CLI/MCP/TUI root entry points. Root entry functions now also declare explicit `None` return types where appropriate.
- Updated the CI test matrix to use `uv sync --dev` and emit a `pytest-cov` coverage report while retaining the Python 3.12 and 3.13 matrix.
- Corrected stale relative documentation links in the agent rule files, `RULES_AES.md`, and `MIGRATION_PYTHON.md`.
- Recorded the current coverage baseline at approximately 61% without introducing an owner-approved failure threshold.

### Fixed

- Fixed `TesseractOCRAdapter.extract_text` return type from `str` to `OcrText` to match `TesseractOCRProtocol` contract and restore Liskov substitution compliance.
- Fixed double-wrap bug in `ImageProcessingProcessor.extract_text` that was constructing `OcrText(value=OcrText(...))` — now returns the adapter result directly.
- Fixed MyPy type mismatch in `VideoContainer.__init__`: declared `_video_understanding` with an explicit `VideoUnderstandingAnalyzer | None` annotation to allow the `None` fallback branch.
- Fixed `CapabilitiesSystemJob.cancel_job` signature to accept `CommandOutput | str` as required by `SystemJobProtocol`, satisfying Liskov substitution.
- Fixed `SystemOrchestrator._handle_get_config` and `_handle_set_config` to wrap raw `str` keys in `ConfigKey` VO before passing to `SystemConfigurationProtocol`.

### Validation

- `bash scripts/gates.sh` passes: Ruff format, Ruff lint (0 violations), MyPy (0 errors in 82 source files), Pytest (44 passed), and AES self-lint (0 violations).
- `uv build` succeeds for the source distribution and wheel.
- All MCP tools verified live against image fixture (`test.jpeg`) and video fixture (`test.mp4`): `vision_status`, `vision_execute` (analyze, ocr, video-info, check-corruption, detect-scenes, detect-motion, analyze-video) all return correct results.

### Security and operational follow-up

- The tracked working tree contains no credential-like values. Earlier Git history still contains a provider credential exposure inherited from the historical security work; provider-side revocation/rotation and any history rewrite remain owner-controlled actions and are intentionally not automated by this mission.
- The publish workflow now verifies the artifact before upload, but no post-publish endpoint health check exists because the repository does not define a deployed service endpoint or staging environment.
- The coverage report is informational only. A minimum coverage threshold and media-performance benchmark require an explicit project-owner decision to avoid imposing an arbitrary gate.
- MCP cancellation remains explicitly reported as unsupported for the current synchronous execution model.


## Historical Changes

### PR #8 — `fix(video): prevent FFmpeg stdin hangs`

- Connected FFmpeg subprocess stdin to `DEVNULL` so media commands cannot wait for terminal input.
- Added a 120-second default timeout, process termination, cleanup, and validation for non-positive timeout values.
- Added regression tests for timeout behavior and cleanup, covering the previously hanging `extract-frames`, `convert`, and `create-gif` workflows.

[PR #8](https://github.com/rakaarwaky/vision-arwaky/pull/8)

### PR #7 — `fix(security): harden config and MCP runtime status`

- Removed the committed API credential from public configuration and added a regression guard against reintroducing secrets.
- Aligned endpoint, model, credential-presence, and package-version reporting with environment/config precedence.
- Added optional authorization to the status endpoint probe without exposing the credential in output.
- Made synchronous cancellation limitations explicit and updated MCP documentation and tests.

[PR #7](https://github.com/rakaarwaky/vision-arwaky/pull/7)

### PR #6 — `docs: add PRD and feature FRDs`

- Added the root product requirements document and feature requirements documents for image, video, OpenCV, CLI, and MCP modules.
- Updated the README and SKILL documentation with the current command surface, smart-video behavior, configuration, testing, and contribution guidance.

[PR #6](https://github.com/rakaarwaky/vision-arwaky/pull/6)

### PR #5 — `fix(video): resolve smart video integration blockers`

- Added bounded smart-video sampling with a maximum of 120 key frames and capped summary prompt input.
- Added temporary-directory cleanup and frame-write validation.
- Exposed `analyze-video` through CLI and MCP discovery and removed the obsolete native VLM path.
- Added regression coverage for sampling bounds, VLM calls, structured output, cleanup, and command discovery.

[PR #5](https://github.com/rakaarwaky/vision-arwaky/pull/5)

### PR #4 — `revert(docs): restore unchanged architecture guides`

- Restored `ARCHITECTURE.md`, `RULES_AES.md`, and `MIGRATION_PYTHON.md` after the documentation scope was narrowed.
- Kept the intended README, SKILL, and CI documentation changes from the preceding documentation work.

[PR #4](https://github.com/rakaarwaky/vision-arwaky/pull/4)

### PR #3 — `docs: refresh AES architecture and developer guides`

- Refreshed developer documentation for the Python AES seven-layer architecture and removed obsolete memory-oriented guidance.
- Standardized local and CI quality-gate commands around `uv`, `scripts/gates.sh`, and `lint-arwaky-cli scan`.
- Updated README, SKILL, and supporting CI documentation to match the active codebase.

[PR #3](https://github.com/rakaarwaky/vision-arwaky/pull/3)

### PR #2 — `feat(aes): AES architecture migration + CI quality gates`

- Migrated the Python workspace to the AES seven-layer architecture with constructor dependency injection and a composition root.
- Introduced protocol contracts, the `RegistryServiceAggregate` facade, feature containers, root dispatching, and console-script entry points under `modules.root_*_entry`.
- Added Ruff, MyPy, Pytest, package-build, and `lint-arwaky-cli` self-lint quality gates, together with the local `scripts/gates.sh` mirror.
- Removed the out-of-scope memory surface and stabilized configuration, FFmpeg path resolution, async execution, and video timeline behavior.

[PR #2](https://github.com/rakaarwaky/vision-arwaky/pull/2)

## References

- [Vision Arwaky repository](https://github.com/rakaarwaky/vision-arwaky)
- [GitHub pull requests](https://github.com/rakaarwaky/vision-arwaky/pulls)
