import json
import os
import asyncio
from src.shared.vision_models_vo import FilePath, LanguageCode, BoundingBox, TimeSegment
from src.image.agent_image_orchestrator import ImageOrchestrator
from src.video.agent_video_orchestrator import VideoOrchestrator
from src.memory.agent_memory_orchestrator import MemoryOrchestrator


def _run_async(coro):
    """Run an async coroutine safely, handling existing event loops."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return _run_async(coro)
    with asyncio.Runner() as runner:
        return runner.run(coro)


def cmd_analyze(args):
    svc = ImageOrchestrator.get_image_processing()
    result = svc.analyze_screenshot(FilePath(value=args.image), prompt=args.prompt)
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
    result = _run_async(svc.extract_frames(FilePath(value=args.video), args.interval))
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
    result = svc.detect_scenes(FilePath(value=args.video), args.threshold)
    print(json.dumps([s.model_dump() for s in result], indent=2))


def cmd_detect_motion(args):
    svc = VideoOrchestrator.get_video_analysis()
    result = svc.detect_motion(FilePath(value=args.video), args.min_area)
    print(json.dumps([e.model_dump() for e in result], indent=2))


def cmd_track(args):
    svc = VideoOrchestrator.get_object_tracking()
    x, y, w, h = [int(v) for v in args.bbox.split(",")]
    bbox = BoundingBox(x=x, y=y, width=w, height=h)
    result = svc.track_object(FilePath(value=args.video), bbox, args.max_frames)
    print(json.dumps([b.model_dump() for b in result], indent=2))


def cmd_timeline(args):
    svc = VideoOrchestrator.get_video_timeline()
    result = _run_async(svc.generate_timeline(FilePath(value=args.video), args.interval))
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
