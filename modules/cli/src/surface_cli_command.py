"""CLI surface — parse args into VOs, delegate to injected aggregate, print JSON."""

import json
import os
from typing import Any

from modules.shared.src.contract_registry_service_aggregate import (
    RegistryServiceAggregate,
)
from modules.shared.src.taxonomy_vision_models_vo import (
    AnalysisPrompt,
    BoundingBox,
    CommandName,
    IntervalSeconds,
    MaxFrames,
    MinArea,
    SceneThreshold,
    TimeSegment,
)

_dispatcher: RegistryServiceAggregate | None = None


def set_cli_dispatcher(dispatcher: RegistryServiceAggregate) -> None:
    """Inject the aggregate facade used by all CLI commands."""
    global _dispatcher
    _dispatcher = dispatcher


def get_dispatcher() -> RegistryServiceAggregate:
    """Return the injected aggregate facade."""
    if _dispatcher is None:
        raise RuntimeError(
            "No dispatcher injected. Call set_cli_dispatcher() before running commands."
        )
    return _dispatcher


def _execute(command: str, kwargs: dict[str, Any]) -> str:
    """Execute a command through the injected aggregate facade."""
    return get_dispatcher().execute_in_process(
        CommandName(value=command), kwargs
    ).value


def _extract_middle_frame(file_path: str) -> str | None:
    """Extract the middle frame of a video file to a temp JPG (returns temp path)."""
    import tempfile

    import cv2 as _cv2

    cap = _cv2.VideoCapture(file_path)
    try:
        total = int(cap.get(_cv2.CAP_PROP_FRAME_COUNT))
        if total <= 0:
            return None
        mid = total // 2
        cap.set(_cv2.CAP_PROP_POS_FRAMES, mid)
        ret, frame = cap.read()
        if not ret:
            return None
        fd, thumb = tempfile.mkstemp(suffix=".jpg")
        os.close(fd)
        _cv2.imwrite(thumb, frame)
        return thumb
    finally:
        cap.release()


def cmd_analyze(args) -> int:
    file_path = args.image
    prompt = AnalysisPrompt(value=args.prompt) if args.prompt else None
    ext = os.path.splitext(file_path)[1].lower()

    # If video file, extract middle frame first
    if ext in (".mp4", ".mov", ".avi", ".mkv", ".webm"):
        thumb = _extract_middle_frame(file_path)
        if thumb is not None:
            try:
                result = _execute("analyze", {"image": thumb, "prompt": prompt.value if prompt else None})
                print(result)
                return 0
            finally:
                os.unlink(thumb)

    result = _execute("analyze", {"image": file_path, "prompt": prompt.value if prompt else None})
    print(result)
    return 0


def cmd_ocr(args) -> int:
    lang = getattr(args, "lang", "eng") or "eng"
    result = _execute("ocr", {"image": args.image, "lang": lang})
    print(result)
    return 0


def cmd_elements(args) -> int:
    result = _execute("elements", {"image": args.image})
    print(result)
    return 0


def cmd_compare(args) -> int:
    result = _execute("compare", {"image1": args.image1, "image2": args.image2})
    print(result)
    return 0


def cmd_video_info(args) -> int:
    result = _execute("video-info", {"video": args.video})
    print(result)
    return 0


def cmd_extract_frames(args) -> int:
    interval = IntervalSeconds(value=float(args.interval))
    result = _execute("extract-frames", {"video": args.video, "interval": interval.value})
    print(result)
    return 0


def cmd_convert(args) -> int:
    result = _execute("convert", {"input_path": args.input, "output_path": args.output})
    print(result)
    return 0


def cmd_check_corruption(args) -> int:
    result = _execute("check-corruption", {"video": args.video})
    print(result)
    return 0


def cmd_create_gif(args) -> int:
    segment = TimeSegment(start=args.start, duration=args.duration)
    result = _execute(
        "create-gif",
        {
            "video": args.video,
            "output_path": args.output,
            "start": segment.start,
            "duration": segment.duration,
        },
    )
    print(result)
    return 0


def cmd_detect_scenes(args) -> int:
    threshold = SceneThreshold(value=float(args.threshold))
    result = _execute("detect-scenes", {"video": args.video, "threshold": threshold.value})
    print(result)
    return 0


def cmd_detect_motion(args) -> int:
    min_area = MinArea(value=int(args.min_area))
    result = _execute("detect-motion", {"video": args.video, "min_area": min_area.value})
    print(result)
    return 0


def cmd_track(args) -> int:
    x, y, w, h = [int(v) for v in args.bbox.split(",")]
    bbox = BoundingBox(x=x, y=y, width=w, height=h)
    max_frames = MaxFrames(value=int(args.max_frames))
    result = _execute(
        "track",
        {
            "video": args.video,
            "bbox": f"{bbox.x},{bbox.y},{bbox.width},{bbox.height}",
            "max_frames": max_frames.value,
        },
    )
    print(result)
    return 0


def cmd_timeline(args) -> int:
    interval = IntervalSeconds(value=float(args.interval))
    result = _execute("timeline", {"video": args.video, "interval": interval.value})
    print(result)
    return 0


def cmd_test(args) -> int:
    """Run the vision-arwaky test suite with optional test image."""
    import subprocess
    import sys

    base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    test_dir = os.path.join(base, "tests")
    fixtures = os.path.join(test_dir, "fixtures")
    default_image = os.path.join(fixtures, "test.jpeg")

    print("=" * 60)
    print("  Vision Arwaky — Test Suite")
    print("=" * 60)
    print(f"  Fixtures: {fixtures}")
    test_image = args.image if args.image else default_image
    print(f"  Test image: {test_image}")
    print()

    # Run pytest
    cmd = [sys.executable, "-m", "pytest", test_dir, "-v"]
    result = subprocess.run(cmd, cwd=base, check=False)

    print()
    if result.returncode == 0:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed")

    # Run AI vision analysis on test image
    if os.path.exists(test_image):
        print()
        print("=" * 60)
        print("  AI Vision Analysis — test image")
        print("=" * 60)
        try:
            analyze_cmd = [
                sys.executable, "-m", "modules.root_cli_entry", "analyze",
                "--image", test_image,
                "--prompt", "Describe this image in detail. What do you see?"
            ]
            vision_result = subprocess.run(analyze_cmd, cwd=base, capture_output=True, text=True, timeout=60, check=False)
            if vision_result.returncode == 0:
                print(vision_result.stdout)
            elif vision_result.stderr:
                # Fallback langsung melalui dispatcher
                result_obj = _execute(
                    "analyze",
                    {"image": test_image, "prompt": "Describe this image in detail. What do you see?"},
                )
                print(result_obj)
        except (OSError, RuntimeError, ValueError) as e:
            print(f"  ⚠ Vision analysis unavailable: {e}")

    # Run AI vision analysis on test video
    test_video = os.path.join(fixtures, "test.mp4")
    if os.path.exists(test_video):
        print()
        print("=" * 60)
        print("  AI Video Analysis — test.mp4")
        print("=" * 60)
        try:
            import cv2

            vproc_info = json.loads(_execute("video-info", {"video": test_video}))
            fps = vproc_info.get("fps") or 30
            print(f"  Metadata: {vproc_info.get('width')}x{vproc_info.get('height')}, {fps:.1f} FPS, {vproc_info.get('frame_count')} frames")
            print()

            # ── Pipeline: Scene + Motion + Uniform ──
            target_frame_indices: set[int] = set()

            # 1. Scene detection — ambil frame pas scene change
            scenes = json.loads(_execute("detect-scenes", {"video": test_video, "threshold": 20.0}))
            for s in scenes:
                idx = int(s["timestamp"] * fps)
                if 0 <= idx < vproc_info.get("frame_count", 0):
                    target_frame_indices.add(idx)
            print(f"  Scene changes: {len(scenes)} → {len(target_frame_indices)} frame(s)")

            # 2. Motion detection — ambil frame dengan motion tertinggi
            events = json.loads(_execute("detect-motion", {"video": test_video, "min_area": 500}))
            events.sort(key=lambda ev: ev["magnitude"], reverse=True)
            for ev in events[:5]:
                idx = int(ev["timestamp"] * fps)
                if 0 <= idx < vproc_info.get("frame_count", 0):
                    target_frame_indices.add(idx)
            print(f"  Motion events: top-{min(5, len(events))} → {len(target_frame_indices)} frame(s)")

            # 3. Uniform sampling — baseline tiap 30 frame
            for idx in range(0, int(vproc_info.get("frame_count", 0)), 30):
                target_frame_indices.add(idx)
            print(f"  Uniform (every 30 frames): {len(target_frame_indices)} total unique frames")

            # ── Extract selected frames ──
            cap = cv2.VideoCapture(test_video)
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            extracted: list[tuple[int, str]] = []
            for idx in sorted(target_frame_indices):
                cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
                ret, frame = cap.read()
                if not ret:
                    continue
                out_path = os.path.join(fixtures, f"frame_{idx:06d}.jpg")
                cv2.imwrite(out_path, frame)
                extracted.append((idx, out_path))
            cap.release()
            print(f"  Extracted {len(extracted)} unique key frames")

            # Check corruption
            corrupted = json.loads(_execute("check-corruption", {"video": test_video}))["corrupted"]
            print(f"  Corrupted: {corrupted}")

            # ── Analyze with VLM ──
            frame_analyses: list[dict] = []
            for i, (idx, frame_path) in enumerate(extracted):
                if not os.path.exists(frame_path):
                    continue
                timestamp = round(idx / fps, 1)
                prompt_text = "Describe this video frame in detail. What objects, people, actions do you see?"
                analysis_result = json.loads(
                    _execute("analyze", {"image": frame_path, "prompt": prompt_text})
                )

                frame_data = {
                    "frame": i + 1,
                    "timestamp_s": timestamp,
                    "source": analysis_result.get("source"),
                    "description": analysis_result.get("text")
                    if analysis_result.get("source") == "llm"
                    else f"(fallback: {len(analysis_result.get('elements', []))} UI elements)",
                }
                frame_analyses.append(frame_data)

                # Print per-frame
                print(f"\n  🎬 Frame {i+1}/{len(extracted)} @ {timestamp}s:")
                text = frame_data["description"][:300] + "..." if len(frame_data["description"]) > 300 else frame_data["description"]
                print(f"     {text}")

                try:
                    os.unlink(frame_path)
                except OSError:
                    pass

            # ── Generate summary from frame descriptions ──
            print("\n  📋 Generating video summary...")
            all_descriptions = "\n".join(
                f"[{f['timestamp_s']}s] {f['description'][:200]}"
                for f in frame_analyses
            )
            summary_prompt = f"Based on these frame-by-frame descriptions, write a brief video summary (3-5 sentences) covering what happens, the setting, people involved, and key actions:\n\n{all_descriptions}"
            try:
                summary_result = json.loads(
                    _execute("analyze", {"image": os.path.join(fixtures, "test.jpeg"), "prompt": summary_prompt})
                )
                video_summary = summary_result.get("text") if summary_result.get("source") == "llm" else "Summary unavailable"
            except (OSError, RuntimeError, ValueError):
                video_summary = "Summary unavailable"

            # ── Final JSON output ──
            output = {
                "video": {
                    "path": test_video,
                    "resolution": f"{vproc_info.get('width')}x{vproc_info.get('height')}",
                    "fps": round(fps, 1),
                    "total_frames": vproc_info.get("frame_count"),
                    "duration_s": round(vproc_info.get("frame_count", 0) / fps, 1) if fps else 0,
                    "corrupted": corrupted,
                },
                "sampling": {
                    "scene_changes": len(scenes),
                    "motion_events": len(events),
                    "uniform_interval": 30,
                    "key_frames_extracted": len(extracted),
                },
                "frames": frame_analyses,
                "summary": video_summary,
            }
            print(f"\n{'=' * 60}")
            print("  JSON Output:")
            print(f"{'=' * 60}")
            print(json.dumps(output, indent=2))

            print("\n  ✅ Video analysis complete")
        except (OSError, RuntimeError, ValueError) as e:
            print(f"  ⚠ Video analysis unavailable: {e}")

    return result.returncode
