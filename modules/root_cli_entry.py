"""Vision root CLI entry point dispatching commands to domain containers."""

import sys
from typing import Union

from modules.cli.src.surface_cli_command import (
    cmd_doctor,
    cmd_image,
    cmd_init,
    cmd_video,
)
from modules.cli.src.surface_cli_controller import create_parser
from modules.image.src.root_image_container import ImageContainer
from modules.shared.src.common.taxonomy_command_vo import CommandDomain
from modules.shared.src.image.contract_image_aggregate import IImageAggregate
from modules.shared.src.system.contract_system_aggregate import ISystemAggregate
from modules.shared.src.video.contract_video_aggregate import IVideoAggregate
from modules.system.src.root_system_container import SystemContainer
from modules.video.src.root_video_container import VideoContainer

CLIOrchestrator = Union[IImageAggregate, ISystemAggregate, IVideoAggregate]

COMMANDS = {
    "init": cmd_init,
    "doctor": cmd_doctor,
    "image": cmd_image,
    "video": cmd_video,
}


def _resolve_orchestrator(
    command: str,
) -> CLIOrchestrator:
    """Return the domain aggregate for the given command."""
    domain = CommandDomain.from_command(command)
    image_container = ImageContainer()
    if domain == CommandDomain.IMAGE:
        return image_container.orchestrator
    if domain == CommandDomain.VIDEO:
        return VideoContainer(llm_port=image_container.llm).orchestrator
    return SystemContainer().orchestrator


def cli() -> None:
    """Parse CLI arguments and dispatch using modular containers."""
    parser = create_parser()
    args = parser.parse_args()

    if not args.command or args.command not in COMMANDS:
        parser.print_help()
        sys.exit(1)

    try:
        orch = _resolve_orchestrator(args.command)
        sys.exit(COMMANDS[args.command](args, orchestrator=orch) or 0)
    except (ValueError, RuntimeError, OSError, KeyError, TypeError) as e:
        sys.stderr.write(f"Error: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    cli()
