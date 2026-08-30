# Plan: video — Architect

## Summary

The `video` feature (v2.0.7) is structurally sound: all seven AES layers are correctly identified by filename, every capability implements its shared contract protocol, the agent implements the `RegistryServiceAggregate` facade purely via injected contracts, and the root container performs composition only. Smart-video bounds (12 key frames, bounded summary prompt, temp cleanup) required by the PRD/FRD are implemented. However, the review found **one critical feature-isolation breach** (the video root lazily imports the image root as a VLM fallback, contradicting the FRD's stated global-root wiring), **systematic DRY violations** where capabilities call raw `cv2` instead of the existing `utility_opencv_ops` pure functions, **two dead artifacts** (an injected `FFmpegVideoProtocol` never used by the orchestrator, and `MAX_EXTRACT_FRAMES` declared but never enforced, leaving `extract-frames` unbounded), and **FRD-mandated validations that are not implemented** (positive interval/threshold VOs, bbox validation). Rule basis: `ARCHITECTURE.md` §4–§11 (7-layer spec) embedded in the corpus.

## Findings

### Capabilities & Agent Compliance (protocol / aggregate check)

| Component | Contract | Status | Note |
| --- | --- | --- | --- |
| `VideoProcessingProcessor` | `VideoProcessingProtocol` | ✅ | All 3 methods implemented |
| `VideoAnalysisAnalyzer` | `VideoAnalysisProtocol` | ✅ | Scene + motion implemented |
| `ObjectTrackingTracker` | `ObjectTrackingProtocol` | ✅ | Graceful loss-of-track handling |
| `FFmpegVideoAdapter` | `FFmpegVideoProtocol` | ✅ | Implementation aligned |
| `VideoUnderstandingAnalyzer` | `VideoUnderstandingProtocol` | ✅ | Bounded sampling + cleanup verified |
| `VideoOrchestrator` | `RegistryServiceAggregate` | ✅ | Aggregate implemented; ports pruned |

### Action Items

- [x] **P0** Remove cross-feature `ImageContainer` fallback from `VideoContainer`; require explicit `llm_port` injection (LB-1).
- [x] **P0** Enforce `MAX_EXTRACT_FRAMES` in `extract_frames` (OR-2 / SC-1).
- [x] **P1** Add `gt=0` validation to `IntervalSeconds`, `SceneThreshold`, `MinArea`, `MaxFrames` (LB-3).
- [x] **P1** Remove unused `ffmpeg` injection from `VideoOrchestrator` and update container wiring (OR-1).
- [x] **P1** Refactor analyzer/understanding capabilities onto `utility_opencv_ops` functions (LB-2).
- [x] **P2** Fix VO import source and logger names in `capabilities_video_understanding.py` (LB-5, NM-2).
- [x] **P2** Move `FFMPEG_TIMEOUT_SECONDS` to taxonomy constants as `FFMPEG_TIMEOUT_S` (NM-4).
- [x] **P2** Remove unused `fps` parameter in `capabilities_video_understanding._extract_frames` (SonarQube S1172).
- [x] **P2** Use SHA-256 in `compute_phash` fallback (SonarQube S4790).
