"""Vision root CLI entry point dispatching commands to domain containers."""

import sys

from modules.cli.src.surface_cli_command import (
    cmd_analyze,
    cmd_analyze_video,
    cmd_check_corruption,
    cmd_compare,
    cmd_detect_motion,
    cmd_detect_scenes,
    cmd_extract_frames,
    cmd_init,
    cmd_ocr,
    cmd_track,
    cmd_video_info,
)
from modules.cli.src.surface_cli_controller import create_parser
from modules.image.src.root_image_container import ImageContainer
from modules.shared.src.contract_registry_service_aggregate import (
    RegistryServiceAggregate,
)
from modules.shared.src.taxonomy_command_vo import CommandDomain
from modules.system.src.root_system_container import SystemContainer
from modules.video.src.root_video_container import VideoContainer

COMMANDS = {
    "init": cmd_init,
    "analyze": cmd_analyze,
    "analyze-video": cmd_analyze_video,
    "ocr": cmd_ocr,
    "compare": cmd_compare,
    "video-info": cmd_video_info,
    "extract-frames": cmd_extract_frames,
    "check-corruption": cmd_check_corruption,
    "detect-scenes": cmd_detect_scenes,
    "detect-motion": cmd_detect_motion,
    "track": cmd_track,
}


def _resolve_orchestrator(
    command: str,
) -> RegistryServiceAggregate:
    """Return the orchestrator for the given command."""
    domain = CommandDomain.from_command(command)
    if domain == CommandDomain.IMAGE:
        return ImageContainer().orchestrator
    if domain == CommandDomain.VIDEO:
        return VideoContainer(llm_port=ImageContainer().llm).orchestrator
    return SystemContainer().orchestrator


def cli() -> None:
    """Parse CLI arguments and dispatch using modular containers."""
    parser = create_parser()
    args = parser.parse_args()

    if not args.command or args.command not in COMMANDS:
        parser.print_help()
        sys.exit(1)

    orch = _resolve_orchestrator(args.command)
    sys.exit(COMMANDS[args.command](args, orchestrator=orch) or 0)


if __name__ == "__main__":
    cli()
