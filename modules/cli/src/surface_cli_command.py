"""CLI surface — parse args into VOs, delegate to injected aggregate, print JSON."""

import os
from typing import Any

from modules.shared.src.contract_registry_service_aggregate import (
    RegistryServiceAggregate,
)
from modules.shared.src.taxonomy_vision_vo import (
    AnalysisPrompt,
    BoundingBox,
    CommandName,
)
from modules.shared.src.utility_frame_extractor import extract_middle_frame

_dispatcher: RegistryServiceAggregate | None = None


def set_cli_dispatcher(dispatcher: RegistryServiceAggregate | None) -> None:
    """Inject the aggregate facade used by CLI commands (optional)."""
    global _dispatcher
    _dispatcher = dispatcher


def get_dispatcher() -> RegistryServiceAggregate | None:
    """Return the injected aggregate facade if present."""
    return _dispatcher


def _execute(
    command: str,
    kwargs: dict[str, Any],
    orchestrator: RegistryServiceAggregate | None = None,
) -> str:
    """Execute a command through the injected or provided orchestrator."""
    orch = orchestrator or _dispatcher
    if orch is None:
        raise RuntimeError(
            "No orchestrator provided. Pass orchestrator or call set_cli_dispatcher()."
        )
    return orch.execute_in_process(CommandName(value=command), kwargs).value


def cmd_init(args, orchestrator: RegistryServiceAggregate | None = None) -> int:
    """Initialize workspace directory, symlinks to XDG, and SKILL.md."""
    target_dir = getattr(args, "target_dir", ".") or "."
    result = _execute("init", {"target_dir": target_dir}, orchestrator=orchestrator)
    print(result)
    return 0


def cmd_analyze(args, orchestrator: RegistryServiceAggregate | None = None) -> int:
    """Analyze an image or a supported video's middle frame."""
    file_path = args.image
    prompt = AnalysisPrompt(value=args.prompt) if args.prompt else None
    ext = os.path.splitext(file_path)[1].lower()

    if ext in (".mp4", ".avi", ".mov", ".mkv", ".webm"):
        thumb_path = extract_middle_frame(file_path)
        if not thumb_path:
            print("Error: Could not extract frame from video for analysis.")
            return 1
        try:
            result = _execute(
                "analyze",
                {
                    "image": thumb_path,
                    "prompt": prompt.value if prompt else None,
                },
                orchestrator=orchestrator,
            )
        finally:
            if os.path.exists(thumb_path):
                os.unlink(thumb_path)
    else:
        result = _execute(
            "analyze",
            {"image": file_path, "prompt": prompt.value if prompt else None},
            orchestrator=orchestrator,
        )

    print(result)
    return 0


def cmd_ocr(args, orchestrator: RegistryServiceAggregate | None = None) -> int:
    """Extract text from an image using OCR."""
    lang = getattr(args, "lang", "eng") or "eng"
    result = _execute(
        "ocr", {"image": args.image, "lang": lang}, orchestrator=orchestrator
    )
    print(result)
    return 0


def cmd_compare(args, orchestrator: RegistryServiceAggregate | None = None) -> int:
    """Compare two screenshots and print structured differences."""
    result = _execute(
        "compare",
        {"image1": args.image1, "image2": args.image2},
        orchestrator=orchestrator,
    )
    print(result)
    return 0


def cmd_video_info(args, orchestrator: RegistryServiceAggregate | None = None) -> int:
    """Print metadata for a video file."""
    result = _execute("video-info", {"video": args.video}, orchestrator=orchestrator)
    print(result)
    return 0


def cmd_extract_frames(
    args, orchestrator: RegistryServiceAggregate | None = None
) -> int:
    """Extract sampled frames from a video file."""
    result = _execute(
        "extract-frames",
        {"video": args.video},
        orchestrator=orchestrator,
    )
    print(result)
    return 0


def cmd_check_corruption(
    args, orchestrator: RegistryServiceAggregate | None = None
) -> int:
    """Check if a video file can be decoded without errors."""
    result = _execute(
        "check-corruption", {"video": args.video}, orchestrator=orchestrator
    )
    print(result)
    return 0


def cmd_detect_scenes(
    args, orchestrator: RegistryServiceAggregate | None = None
) -> int:
    """Detect scene transitions in a video file."""
    result = _execute(
        "detect-scenes",
        {"video": args.video},
        orchestrator=orchestrator,
    )
    print(result)
    return 0


def cmd_detect_motion(
    args, orchestrator: RegistryServiceAggregate | None = None
) -> int:
    """Detect significant motion events in a video file."""
    result = _execute(
        "detect-motion",
        {"video": args.video},
        orchestrator=orchestrator,
    )
    print(result)
    return 0


def cmd_track(args, orchestrator: RegistryServiceAggregate | None = None) -> int:
    """Track an object across frames using an initial bounding box."""
    try:
        x, y, w, h = map(int, args.bbox.split(","))
    except ValueError:
        print(f"Error: Invalid bbox format '{args.bbox}'. Expected 'X,Y,W,H'")
        return 1

    bbox_vo = BoundingBox(x=x, y=y, width=w, height=h)
    result = _execute(
        "track",
        {
            "video": args.video,
            "bbox": f"{bbox_vo.x},{bbox_vo.y},{bbox_vo.width},{bbox_vo.height}",
        },
        orchestrator=orchestrator,
    )
    print(result)
    return 0


def cmd_analyze_video(
    args, orchestrator: RegistryServiceAggregate | None = None
) -> int:
    """Run VLM-backed smart video analysis on selected key frames."""
    prompt = AnalysisPrompt(value=args.prompt) if args.prompt else None
    result = _execute(
        "analyze-video",
        {"video": args.video, "prompt": prompt.value if prompt else None},
        orchestrator=orchestrator,
    )
    print(result)
    return 0
