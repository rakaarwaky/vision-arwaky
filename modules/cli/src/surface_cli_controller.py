import argparse


def create_parser() -> argparse.ArgumentParser:
    """Create the argparse parser for all public CLI commands."""

    parser = argparse.ArgumentParser(
        prog="vision",
        description="Vision — Unified Image & Video Intelligence CLI",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # --- Image commands ---
    analyze = subparsers.add_parser(
        "analyze", help="Analyze screenshot or image with AI vision"
    )
    analyze.add_argument("--image", required=True, help="Image path")
    analyze.add_argument("--prompt", default=None, help="Custom analysis prompt")

    ocr = subparsers.add_parser("ocr", help="Extract text from image using OCR")
    ocr.add_argument("--image", required=True, help="Image path")
    ocr.add_argument("--lang", default="eng", help="OCR language (default: eng)")

    compare = subparsers.add_parser("compare", help="Compare two screenshots")
    compare.add_argument("--image1", required=True, help="First image path")
    compare.add_argument("--image2", required=True, help="Second image path")

    # --- Video commands ---
    video_info = subparsers.add_parser("video-info", help="Get video metadata")
    video_info.add_argument("--video", required=True, help="Video path")

    extract = subparsers.add_parser("extract-frames", help="Extract frames from video")
    extract.add_argument("--video", required=True, help="Video path")

    corruption = subparsers.add_parser(
        "check-corruption", help="Check if video is corrupted"
    )
    corruption.add_argument("--video", required=True, help="Video path")

    # --- Analysis commands ---
    scenes = subparsers.add_parser(
        "detect-scenes", help="Detect scene changes in video"
    )
    scenes.add_argument("--video", required=True, help="Video path")

    motion = subparsers.add_parser(
        "detect-motion", help="Detect motion events in video"
    )
    motion.add_argument("--video", required=True, help="Video path")

    track = subparsers.add_parser("track", help="Track object through video")
    track.add_argument("--video", required=True, help="Video path")
    track.add_argument("--bbox", required=True, help="Initial bounding box: X,Y,W,H")

    analyze_video = subparsers.add_parser(
        "analyze-video", help="Smart video understanding (key-frame + VLM)"
    )
    analyze_video.add_argument("--video", required=True, help="Video path")
    analyze_video.add_argument(
        "--prompt", default=None, help="Custom per-frame analysis prompt"
    )

    return parser

