import argparse
from src.contract import RegistryServiceAggregate

def create_parser() -> argparse.ArgumentParser:
    # Dummy reference to satisfy linter type checking and imports
    _unused = RegistryServiceAggregate
    
    parser = argparse.ArgumentParser(
        prog="vision",
        description="Vision — Unified Image & Video Intelligence CLI",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # --- Image commands ---
    analyze = subparsers.add_parser("analyze", help="Analyze screenshot for UI elements and text")
    analyze.add_argument("--image", required=True, help="Image path")
    analyze.add_argument("--prompt", default=None, help="Custom analysis prompt")

    ocr = subparsers.add_parser("ocr", help="Extract text from image using OCR")
    ocr.add_argument("--image", required=True, help="Image path")
    ocr.add_argument("--lang", default="eng", help="OCR language (default: eng)")

    elements = subparsers.add_parser("elements", help="Find UI elements in image")
    elements.add_argument("--image", required=True, help="Image path")

    compare = subparsers.add_parser("compare", help="Compare two screenshots")
    compare.add_argument("--image1", required=True, help="First image path")
    compare.add_argument("--image2", required=True, help="Second image path")

    # --- Video commands ---
    video_info = subparsers.add_parser("video-info", help="Get video metadata")
    video_info.add_argument("--video", required=True, help="Video path")

    extract = subparsers.add_parser("extract-frames", help="Extract frames from video")
    extract.add_argument("--video", required=True, help="Video path")
    extract.add_argument("--interval", type=float, default=1.0, help="Frame interval in seconds")

    convert = subparsers.add_parser("convert", help="Convert video format")
    convert.add_argument("--input", required=True, help="Input video path")
    convert.add_argument("--output", required=True, help="Output video path")

    corruption = subparsers.add_parser("check-corruption", help="Check if video is corrupted")
    corruption.add_argument("--video", required=True, help="Video path")

    gif = subparsers.add_parser("create-gif", help="Create GIF from video segment")
    gif.add_argument("--video", required=True, help="Video path")
    gif.add_argument("--output", required=True, help="Output GIF path")
    gif.add_argument("--start", type=float, default=None, help="Start time in seconds")
    gif.add_argument("--duration", type=float, default=None, help="Duration in seconds")

    # --- Analysis commands ---
    scenes = subparsers.add_parser("detect-scenes", help="Detect scene changes in video")
    scenes.add_argument("--video", required=True, help="Video path")
    scenes.add_argument("--threshold", type=float, default=30.0, help="Scene change threshold")

    motion = subparsers.add_parser("detect-motion", help="Detect motion events in video")
    motion.add_argument("--video", required=True, help="Video path")
    motion.add_argument("--min-area", type=int, default=500, help="Minimum motion area")

    track = subparsers.add_parser("track", help="Track object through video")
    track.add_argument("--video", required=True, help="Video path")
    track.add_argument("--bbox", required=True, help="Initial bounding box: X,Y,W,H")
    track.add_argument("--max-frames", type=int, default=300, help="Max frames to track")

    timeline = subparsers.add_parser("timeline", help="Generate video timeline")
    timeline.add_argument("--video", required=True, help="Video path")
    timeline.add_argument("--interval", type=int, default=5, help="Interval in seconds")

    # --- Memory commands ---
    memory = subparsers.add_parser("memory", help="Visual memory operations")
    mem_sub = memory.add_subparsers(dest="memory_cmd")

    mem_store = mem_sub.add_parser("store", help="Store image in memory")
    mem_store.add_argument("--image", required=True, help="Image path")
    mem_store.add_argument("--label", required=True, help="Label for the image")

    mem_search = mem_sub.add_parser("search", help="Search similar images")
    mem_search.add_argument("--query", required=True, help="Query image path")
    mem_search.add_argument("--max-distance", type=int, default=15, help="Max hamming distance")

    mem_sub.add_parser("list", help="List all stored images")

    return parser
