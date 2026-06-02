import sys
from src.surfaces import (
    create_parser,
    cmd_analyze,
    cmd_ocr,
    cmd_elements,
    cmd_compare,
    cmd_video_info,
    cmd_extract_frames,
    cmd_convert,
    cmd_check_corruption,
    cmd_create_gif,
    cmd_detect_scenes,
    cmd_detect_motion,
    cmd_track,
    cmd_timeline,
    cmd_memory_store,
    cmd_memory_search,
    cmd_memory_list,
)


def cli():
    """Entry point for the vision CLI."""
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
    }

    if args.command == "memory":
        if args.memory_cmd == "store":
            cmd_memory_store(args)
        elif args.memory_cmd == "search":
            cmd_memory_search(args)
        elif args.memory_cmd == "list":
            cmd_memory_list()
        else:
            print("vision memory: requires subcommand (store|search|list)")
            sys.exit(1)
    elif args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    cli()
