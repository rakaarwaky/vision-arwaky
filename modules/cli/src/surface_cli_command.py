"""CLI surface — parse args into VOs, delegate to injected aggregate, print JSON."""

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
    return get_dispatcher().execute_in_process(CommandName(value=command), kwargs).value


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
                result = _execute(
                    "analyze",
                    {"image": thumb, "prompt": prompt.value if prompt else None},
                )
                print(result)
                return 0
            finally:
                os.unlink(thumb)

    result = _execute(
        "analyze", {"image": file_path, "prompt": prompt.value if prompt else None}
    )
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
    result = _execute(
        "extract-frames", {"video": args.video, "interval": interval.value}
    )
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
    result = _execute(
        "detect-scenes", {"video": args.video, "threshold": threshold.value}
    )
    print(result)
    return 0


def cmd_detect_motion(args) -> int:
    min_area = MinArea(value=int(args.min_area))
    result = _execute(
        "detect-motion", {"video": args.video, "min_area": min_area.value}
    )
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


def cmd_analyze_video(args) -> int:
    result = _execute(
        "analyze-video",
        {
            "video": args.video,
            "prompt": getattr(args, "prompt", None),
            "interval": float(getattr(args, "interval", 30.0)),
            "scene_threshold": float(getattr(args, "scene_threshold", 20.0)),
            "min_area": int(getattr(args, "min_area", 500)),
        },
    )
    print(result)
    return 0


def cmd_test(args) -> int:
    """Run the vision-arwaky test suite with optional test image."""
    try:
        import importlib

        pytest: Any = importlib.import_module("pytest")
    except ImportError:
        print("❌ pytest is not installed; install it to run the test command")
        return 1

    # modules/cli/src/surface_cli_command.py -> repo root
    base = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    )
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

    # Run pytest in-process; the test directory is a trusted repository path.
    result_code = pytest.main([test_dir, "-v"])

    print()
    if result_code == 0:
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
            # Reuse the injected dispatcher instead of spawning a second CLI process.
            vision_result = _execute(
                "analyze",
                {
                    "image": test_image,
                    "prompt": "Describe this image in detail. What do you see?",
                },
            )
            print(vision_result)
        except (OSError, RuntimeError, ValueError) as e:
            print(f"  ⚠ Vision analysis unavailable: {e}")

    # Run AI video understanding on test video.
    # Delegates to the VideoUnderstanding capability in the video feature
    # layer (scene + motion + uniform key-frame selection, per-frame VLM,
    # and synthesized summary) instead of duplicating the logic here.
    test_video = os.path.join(fixtures, "test.mp4")
    if os.path.exists(test_video):
        print()
        print("=" * 60)
        print("  AI Video Understanding — test.mp4")
        print("=" * 60)
        try:
            video_result = _execute(
                "analyze-video",
                {
                    "video": test_video,
                    "prompt": (
                        "Describe this video frame in detail. "
                        "What objects, people, actions do you see?"
                    ),
                    "interval": 30.0,
                    "scene_threshold": 20.0,
                    "min_area": 500,
                },
            )
            print(video_result)
            print("\n  ✅ Video analysis complete")
        except (OSError, RuntimeError, ValueError) as e:
            print(f"  ⚠ Video analysis unavailable: {e}")

    return result_code
