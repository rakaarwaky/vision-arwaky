import sys

from modules.cli.src.surface_cli_command import (
    cmd_analyze,
    cmd_check_corruption,
    cmd_compare,
    cmd_convert,
    cmd_create_gif,
    cmd_detect_motion,
    cmd_detect_scenes,
    cmd_elements,
    cmd_extract_frames,
    cmd_ocr,
    cmd_test,
    cmd_timeline,
    cmd_track,
    cmd_video_info,
    set_cli_dispatcher,
)
from modules.cli.src.surface_cli_controller import create_parser
from modules.root_composition_container import build


def cli():
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    commands = {
        "analyze": cmd_analyze,
        "ocr": cmd_ocr,
        "elements": cmd_elements,
        "compare": cmd_compare,
        "video-info": cmd_video_info,
        "extract-frames": cmd_extract_frames,
        "convert": cmd_convert,
        "check-corruption": cmd_check_corruption,
        "create-gif": cmd_create_gif,
        "detect-scenes": cmd_detect_scenes,
        "detect-motion": cmd_detect_motion,
        "track": cmd_track,
        "timeline": cmd_timeline,
        "test": cmd_test,
    }

    if args.command not in commands:
        parser.print_help()
        sys.exit(1)

    graph = build()
    set_cli_dispatcher(graph["dispatcher"])
    sys.exit(commands[args.command](args) or 0)


if __name__ == "__main__":
    cli()
