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
    import importlib
    import tempfile

    cv2: Any = importlib.import_module("cv2")
    cap = cv2.VideoCapture(file_path)
    try:
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if total <= 0:
            return None
        mid = total // 2
        cap.set(cv2.CAP_PROP_POS_FRAMES, mid)
        ret, frame = cap.read()
        if not ret:
            return None
        fd, thumb = tempfile.mkstemp(suffix=".jpg")
        os.close(fd)
        cv2.imwrite(thumb, frame)
        return thumb
    finally:
        cap.release()


def cmd_analyze(args) -> int:
    """Analyze an image or a supported video's middle frame."""
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
    """Extract text from an image with Tesseract OCR."""
    lang = getattr(args, "lang", "eng") or "eng"
    result = _execute("ocr", {"image": args.image, "lang": lang})
    print(result)
    return 0


def cmd_compare(args) -> int:
    """Compare two screenshots and print structured differences."""
    result = _execute("compare", {"image1": args.image1, "image2": args.image2})
    print(result)
    return 0


def cmd_video_info(args) -> int:
    """Print metadata for a video file."""
    result = _execute("video-info", {"video": args.video})
    print(result)
    return 0


def cmd_extract_frames(args) -> int:
    """Extract sampled frames from a video file."""
    result = _execute("extract-frames", {"video": args.video})
    print(result)
    return 0


def cmd_check_corruption(args) -> int:
    """Check whether a video can be opened and decoded."""
    result = _execute("check-corruption", {"video": args.video})
    print(result)
    return 0


def cmd_detect_scenes(args) -> int:
    """Detect scene changes in a video."""
    result = _execute("detect-scenes", {"video": args.video})
    print(result)
    return 0


def cmd_detect_motion(args) -> int:
    """Detect motion events in a video."""
    result = _execute("detect-motion", {"video": args.video})
    print(result)
    return 0


def cmd_track(args) -> int:
    """Track an object from an initial bounding box through a video."""
    x, y, w, h = [int(v) for v in args.bbox.split(",")]
    bbox = BoundingBox(x=x, y=y, width=w, height=h)
    result = _execute(
        "track",
        {
            "video": args.video,
            "bbox": f"{bbox.x},{bbox.y},{bbox.width},{bbox.height}",
        },
    )
    print(result)
    return 0


def cmd_analyze_video(args) -> int:
    """Analyze bounded representative video frames with a VLM."""
    result = _execute(
        "analyze-video",
        {
            "video": args.video,
            "prompt": getattr(args, "prompt", None),
        },
    )
    print(result)
    return 0

