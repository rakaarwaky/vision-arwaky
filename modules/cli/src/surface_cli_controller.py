import argparse

from modules.shared.src.common.utility_version_resolver import get_package_version

_HELP_IMAGE_PATH = "Image path"
_HELP_VIDEO_PATH = "Video path"


def create_parser() -> argparse.ArgumentParser:
    """Create the argparse parser for all public CLI commands."""
    pkg_version = get_package_version()
    parser = argparse.ArgumentParser(
        prog="vision-arwaky-cli",
        description="Vision Arwaky — Unified Image & Video Intelligence CLI",
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {pkg_version}",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # --- Workspace commands ---
    init_cmd = subparsers.add_parser(
        "init",
        help="Initialize workspace directory structure and XDG symlinks",
    )
    init_cmd.add_argument(
        "target_dir",
        nargs="?",
        default=".",
        help="Target workspace directory (default: .)",
    )

    # --- Image commands ---
    image = subparsers.add_parser("image", help="Analyze image with AI vision")
    image.add_argument(
        "image",
        help="Image path",
    )

    # --- Video commands ---
    video = subparsers.add_parser(
        "video", help="Smart video understanding (key-frame + VLM)"
    )
    video.add_argument(
        "video",
        help="Video path",
    )

    # --- System commands ---
    subparsers.add_parser("doctor", help="Check system dependencies and readiness")

    return parser
