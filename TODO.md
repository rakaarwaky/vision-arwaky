# Autonomous Engineering TODO

This file is the working feature matrix and acceptance checklist for the end-to-end engineering mission. Status values are `PASS`, `OBSERVED`, `GAP`, or `PENDING` and must be revalidated before delivery.

## Feature Matrix

| Priority | Feature or requirement | Source | Current evidence | Status | Next validation or action |
|---|---|---|---|---|---|
| P0 | CLI exposes all image, video, smart-video, and test commands | PRD P0; CLI FRD | Parser contains 15 commands; all help paths pass in final E2E suite | PASS | Preserve command/help parity in future changes |
| P0 | MCP exposes execute, discovery, help, status, and cancellation tools | PRD P0; MCP FRD | Five tools are registered and MCP smoke tests pass | PASS | Re-run tool-level integration tests |
| P0 | MCP command catalog includes every image/video command | PRD P0; MCP FRD | 4 image + 10 video commands including `analyze-video` are present | PASS | Compare catalog with root dispatcher constants |
| P0 | Root composition routes public execution through injected graph | Architecture; PRD P0 | `RootDispatcher` and feature containers wire shared ports; AES self-lint passes | PASS | Preserve composition boundary in future changes |
| P0 | Smart-video is bounded and cleans temporary artifacts | PRD P0; Video FRD | Frame cap, prompt bound, fallback, cleanup tests exist | PASS | Re-run focused and E2E smart-video tests |
| P0 | Package, test matrix, and self-lint pass | PRD; CI workflow | Local gates, full tests, and `uv build` pass; CI has Python 3.12/3.13 matrix | PASS | Preserve all gates on future changes |
| P1 | Deterministic image/video commands work without VLM | PRD P1; FRDs | Final E2E suite passes deterministic workflows with an unavailable VLM endpoint | PASS | Preserve deterministic fallback coverage |
| P1 | Status distinguishes config, dependencies, endpoint, and credential presence | MCP FRD | `vision_status` reports configured endpoint, HTTP status, version, and boolean credential presence | PASS | Test env overrides and missing system binaries |
| P1 | Cancellation supports active asynchronous work | MCP FRD | Current path is synchronous and returns `supported: false` | OBSERVED | Keep explicit limitation or implement async job controller |
| P1 | Public config contains no credentials and secret history is remediated | PRD security; runtime audit | Current tree sanitized; old history still contains credential exposure | GAP | Rotate/revoke provider credential and evaluate history rewrite |
| P1 | CLI E2E is automated in CI | Mission QA; CI workflow | Dedicated `cli-e2e` job runs `tests/test_cli_e2e.py` with OpenCV, Tesseract, and FFmpeg | PASS | Keep the job required for pull requests |
| P1 | Release has staging or post-publish health validation | Mission deployment | Publish workflow now smoke-tests the wheel before upload; no post-publish endpoint health check exists | GAP | Add a post-publish verification owner/path when a deployment endpoint exists |
| P2 | Documentation references are complete and current | add-docs-python; README/MIGRATION | Public docstring audit reports none; stale-link audit reports none | PASS | Re-run documentation audit before releases |
| P2 | Lint/type tools are declared in project dev dependencies | Mission setup | `dev` group declares pytest, pytest-cov, Ruff, and MyPy; `uv.lock` is updated | PASS | Use `uv sync --dev` for quality workflows |
| P2 | Dependency warning is eliminated or pinned/understood | Runtime audit | Pydantic `lifespan` warning appears on MCP import | OBSERVED | Identify upstream compatibility and add a regression guard or pin |
| P2 | Coverage and performance thresholds are enforced | Mission QA | CI now emits pytest-cov report; local baseline is 61%; no fail threshold or benchmark gate is enforced | OBSERVED | Set an owner-approved coverage threshold and add targeted media benchmarks |

## Acceptance Checklist

### Context and architecture

- [x] PRD, all feature FRDs, README, SKILL, ARCHITECTURE, RULES_AES, and migration guidance match the implementation.
- [x] Every public command maps to one parser registration, one dispatcher route, and one documented contract.
- [x] Root composition is the only concrete dependency wiring layer.
- [x] No surface imports capabilities directly, no agent imports capabilities directly, and no forbidden AES imports remain.

### Implementation and security

- [x] Current tracked files contain no credential-like values.
- [ ] Provider credential exposure from Git history has an owner-approved revoke/rotate and cleanup decision.
- [x] FFmpeg subprocesses use non-interactive stdin, bounded execution, and process cleanup.
- [x] OpenCV capture resources and smart-video temporary files are released on success and failure.
- [x] External VLM failures produce controlled fallback or diagnostic errors.

### Quality assurance

- [x] Ruff format check passes.
- [x] Ruff lint passes.
- [x] Mypy passes.
- [x] Pytest passes on the configured Python 3.12 and 3.13 CI matrix.
- [x] AES self-lint reports zero violations.
- [x] `uv build` succeeds.
- [x] Fixture-backed E2E covers all CLI commands and uses `stdin=subprocess.DEVNULL` for subprocess isolation.
- [ ] MCP discovery, help, status, and error contracts are tested.

### Delivery readiness

- [x] CI checks all quality gates and the dedicated CLI E2E suite.
- [x] Package artifact can be installed and smoke-tested from a clean environment in the publish workflow.
- [ ] Release workflow has a documented staging or post-publish verification path.
- [x] Changelog records behavior, security, and operational changes.
