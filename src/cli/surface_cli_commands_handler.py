import json
import os
import asyncio
from src.shared.vision_models_vo import FilePath, LanguageCode, BoundingBox, TimeSegment, IntervalSeconds, AnalysisPrompt
from src.image.agent_image_orchestrator import ImageOrchestrator
from src.video.agent_video_orchestrator import VideoOrchestrator
from src.memory.agent_memory_orchestrator import MemoryOrchestrator


def _run_async(coro):
    """Run an async coroutine safely, handling existing event loops."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    with asyncio.Runner() as runner:
        return runner.run(coro)


def cmd_analyze(args):
    svc = ImageOrchestrator.get_image_processing()
    from src.shared.vision_models_vo import AnalysisPrompt
    prompt = AnalysisPrompt(value=args.prompt) if args.prompt else None

    file_path = args.image
    ext = os.path.splitext(file_path)[1].lower()

    # If video file, extract middle frame first
    if ext in (".mp4", ".mov", ".avi", ".mkv", ".webm"):
        import cv2 as _cv2
        cap = _cv2.VideoCapture(file_path)
        total = int(cap.get(_cv2.CAP_PROP_FRAME_COUNT))
        if total > 0:
            mid = total // 2
            cap.set(_cv2.CAP_PROP_POS_FRAMES, mid)
            ret, frame = cap.read()
            cap.release()
            if ret:
                import tempfile
                fd, thumb = tempfile.mkstemp(suffix=".jpg")
                os.close(fd)
                _cv2.imwrite(thumb, frame)
                result = svc.analyze_screenshot(FilePath(value=thumb), prompt=prompt)
                os.unlink(thumb)
                print(json.dumps(result.model_dump(), indent=2))
                return
        cap.release()

    # Default: image file
    result = svc.analyze_screenshot(FilePath(value=file_path), prompt=prompt)
    print(json.dumps(result.model_dump(), indent=2))


def cmd_ocr(args):
    svc = ImageOrchestrator.get_image_processing()
    lang_val = getattr(args, "lang", "eng") or "eng"
    result = svc.extract_text(FilePath(value=args.image), LanguageCode(value=lang_val))
    print(result.value)


def cmd_elements(args):
    svc = ImageOrchestrator.get_image_processing()
    result = svc.find_elements(FilePath(value=args.image))
    print(json.dumps([e.model_dump() for e in result], indent=2))


def cmd_compare(args):
    svc = ImageOrchestrator.get_image_processing()
    result = svc.compare_screenshots(FilePath(value=args.image1), FilePath(value=args.image2))
    print(json.dumps(result, indent=2))


def cmd_video_info(args):
    svc = VideoOrchestrator.get_video_processing()
    result = svc.get_info(FilePath(value=args.video))
    print(json.dumps(result.model_dump(), indent=2))


def cmd_extract_frames(args):
    svc = VideoOrchestrator.get_video_processing()
    interval = IntervalSeconds(value=float(args.interval))
    result = _run_async(svc.extract_frames(FilePath(value=args.video), interval))
    print(json.dumps([r.value for r in result], indent=2))


def cmd_convert(args):
    svc = VideoOrchestrator.get_video_processing()
    result = _run_async(svc.convert_format(FilePath(value=args.input), FilePath(value=args.output)))
    print(json.dumps({"success": result}))


def cmd_check_corruption(args):
    svc = VideoOrchestrator.get_video_processing()
    result = svc.check_corruption(FilePath(value=args.video))
    print(json.dumps({"corrupted": result}))


def cmd_create_gif(args):
    svc = VideoOrchestrator.get_video_processing()
    segment = TimeSegment(start=args.start, duration=args.duration)
    result = _run_async(svc.create_gif(FilePath(value=args.video), FilePath(value=args.output), segment))
    print(json.dumps({"success": result}))


def cmd_detect_scenes(args):
    svc = VideoOrchestrator.get_video_analysis()
    from src.shared.vision_models_vo import SceneThreshold
    threshold = SceneThreshold(value=float(args.threshold))
    result = svc.detect_scenes(FilePath(value=args.video), threshold)
    print(json.dumps([s.model_dump() for s in result], indent=2))


def cmd_detect_motion(args):
    svc = VideoOrchestrator.get_video_analysis()
    from src.shared.vision_models_vo import MinArea
    min_area = MinArea(value=int(args.min_area))
    result = svc.detect_motion(FilePath(value=args.video), min_area)
    print(json.dumps([e.model_dump() for e in result], indent=2))


def cmd_track(args):
    svc = VideoOrchestrator.get_object_tracking()
    from src.shared.vision_models_vo import MaxFrames
    x, y, w, h = [int(v) for v in args.bbox.split(",")]
    bbox = BoundingBox(x=x, y=y, width=w, height=h)
    max_frames = MaxFrames(value=int(args.max_frames))
    result = svc.track_object(FilePath(value=args.video), bbox, max_frames)
    print(json.dumps([b.model_dump() for b in result], indent=2))


def cmd_timeline(args):
    svc = VideoOrchestrator.get_video_timeline()
    from src.shared.vision_models_vo import IntervalSeconds
    interval = IntervalSeconds(value=float(args.interval))
    result = _run_async(svc.generate_timeline(FilePath(value=args.video), interval))
    print(json.dumps(result.model_dump(), indent=2))


def cmd_memory_store(args):
    svc = MemoryOrchestrator.get_visual_memory()
    result = svc.remember_image(FilePath(value=args.image), args.label)
    print(json.dumps(result.model_dump(), indent=2))


def cmd_memory_search(args):
    svc = MemoryOrchestrator.get_visual_memory()
    result = svc.find_similar_images(FilePath(value=args.query), args.max_distance)
    print(json.dumps([r.model_dump() for r in result], indent=2))


def cmd_memory_list():
    memory_dir = os.path.join(os.path.expanduser("~/.cache"), "vision-arwaky", "memory")
    index_file = os.path.join(memory_dir, "index.json")
    if os.path.exists(index_file):
        with open(index_file) as f:
            data = json.load(f)
        print(json.dumps(data, indent=2))
    else:
        print(json.dumps({}))


def cmd_test(args):
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
    result = subprocess.run(cmd, cwd=base)

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
                sys.executable, "-m", "src.cli_entry", "analyze",
                "--image", test_image,
                "--prompt", "Describe this image in detail. What do you see?"
            ]
            vision_result = subprocess.run(analyze_cmd, cwd=base, capture_output=True, text=True, timeout=60)
            if vision_result.returncode == 0:
                print(vision_result.stdout)
            elif vision_result.stderr:
                # fallback langsung
                from src.image.agent_image_orchestrator import ImageOrchestrator
                from src.shared.vision_models_vo import FilePath, AnalysisPrompt
                svc = ImageOrchestrator.get_image_processing()
                prompt = AnalysisPrompt(value="Describe this image in detail. What do you see?")
                result_obj = svc.analyze_screenshot(FilePath(value=test_image), prompt=prompt)
                import json
                print(json.dumps(result_obj.model_dump(), indent=2))
        except Exception as e:
            print(f"  ⚠ Vision analysis unavailable: {e}")

    # Run AI vision analysis on test video
    test_video = os.path.join(fixtures, "test.mp4")
    if os.path.exists(test_video):
        print()
        print("=" * 60)
        print("  AI Video Analysis — test.mp4")
        print("=" * 60)
        try:
            from src.video.agent_video_orchestrator import VideoOrchestrator
            from src.image.agent_image_orchestrator import ImageOrchestrator
            from src.shared.vision_models_vo import (
                FilePath, IntervalSeconds, AnalysisPrompt,
                SceneThreshold, MinArea,
            )
            import asyncio
            import cv2
            import json

            vproc = VideoOrchestrator.get_video_processing()
            aproc = VideoOrchestrator.get_video_analysis()
            info = vproc.get_info(FilePath(value=test_video))
            fps = info.fps or 30
            print(f"  Metadata: {info.width}x{info.height}, {info.fps:.1f} FPS, {info.frame_count} frames")
            print()

            # ── Pipeline: Scene + Motion + Uniform ──
            target_frame_indices: set[int] = set()

            # 1. Scene detection — ambil frame pas scene change
            scenes = aproc.detect_scenes(FilePath(value=test_video), SceneThreshold(value=20.0))
            for s in scenes:
                idx = int(s.timestamp * fps)
                if 0 <= idx < info.frame_count:
                    target_frame_indices.add(idx)
            print(f"  Scene changes: {len(scenes)} → {len(target_frame_indices)} frame(s)")

            # 2. Motion detection — ambil frame dengan motion tertinggi
            events = aproc.detect_motion(FilePath(value=test_video), MinArea(value=500))
            events.sort(key=lambda e: e.magnitude, reverse=True)
            for e in events[:5]:
                idx = int(e.timestamp * fps)
                if 0 <= idx < info.frame_count:
                    target_frame_indices.add(idx)
            print(f"  Motion events: top-{min(5, len(events))} → {len(target_frame_indices)} frame(s)")

            # 3. Uniform sampling — baseline tiap 30 frame
            for idx in range(0, info.frame_count, 30):
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
            corrupted = vproc.check_corruption(FilePath(value=test_video))
            print(f"  Corrupted: {corrupted}")

            # ── Analyze with VLM ──
            img_proc = ImageOrchestrator.get_image_processing()
            frame_analyses: list[dict] = []
            for i, (idx, frame_path) in enumerate(extracted):
                if not os.path.exists(frame_path):
                    continue
                timestamp = round(idx / fps, 1)
                prompt_obj = AnalysisPrompt(value="Describe this video frame in detail. What objects, people, actions do you see?")
                analysis_result = img_proc.analyze_screenshot(FilePath(value=frame_path), prompt=prompt_obj)

                frame_data = {
                    "frame": i + 1,
                    "timestamp_s": timestamp,
                    "source": analysis_result.source,
                    "description": analysis_result.text if analysis_result.source == "llm" else f"(fallback: {len(analysis_result.elements)} UI elements)",
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
            summary_prompt = AnalysisPrompt(value=f"Based on these frame-by-frame descriptions, write a brief video summary (3-5 sentences) covering what happens, the setting, people involved, and key actions:\n\n{all_descriptions}")
            try:
                summary_result = img_proc.analyze_screenshot(
                    FilePath(value=fixtures + "/test.jpeg"),
                    prompt=summary_prompt,
                )
                video_summary = summary_result.text if summary_result.source == "llm" else "Summary unavailable"
            except Exception:
                video_summary = "Summary unavailable"

            # ── Final JSON output ──
            output = {
                "video": {
                    "path": test_video,
                    "resolution": f"{info.width}x{info.height}",
                    "fps": round(info.fps, 1),
                    "total_frames": info.frame_count,
                    "duration_s": round(info.frame_count / fps, 1) if fps else 0,
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
        except Exception as e:
            print(f"  ⚠ Video analysis unavailable: {e}")

    return result.returncode
