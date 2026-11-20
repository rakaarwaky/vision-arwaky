"""CLI surface — parse args into VOs, delegate to injected aggregate, print JSON."""

from modules.shared.src.contract_registry_service_aggregate import (
    IRegistryServiceAggregate,
)
from modules.shared.src.taxonomy_vision_vo import CommandName

_dispatcher: IRegistryServiceAggregate | None = None


def set_cli_dispatcher(dispatcher: IRegistryServiceAggregate | None) -> None:
    """Inject the aggregate facade used by CLI commands (optional)."""
    global _dispatcher
    _dispatcher = dispatcher


def get_dispatcher() -> IRegistryServiceAggregate | None:
    """Return the injected aggregate facade if present."""
    return _dispatcher


def _execute(
    command: str,
    kwargs: dict,
    orchestrator: IRegistryServiceAggregate | None = None,
) -> str:
    """Execute a command through the injected or provided orchestrator."""
    orch = orchestrator or _dispatcher
    if orch is None:
        raise RuntimeError(
            "No orchestrator provided. Pass orchestrator or call set_cli_dispatcher()."
        )
    return orch.execute_in_process(CommandName(value=command), kwargs).value


def cmd_init(args, orchestrator: IRegistryServiceAggregate | None = None) -> int:
    """Initialize workspace directory and symlinks to XDG."""
    target_dir = getattr(args, "target_dir", ".") or "."
    result = _execute("init", {"target_dir": target_dir}, orchestrator=orchestrator)
    print(result)
    return 0


def cmd_image(args, orchestrator: IRegistryServiceAggregate | None = None) -> int:
    """Analyze an image with AI vision."""
    image_path = args.image
    result = _execute("analyze", {"image": image_path}, orchestrator=orchestrator)
    print(result)
    return 0


def cmd_video(args, orchestrator: IRegistryServiceAggregate | None = None) -> int:
    """Run VLM-backed smart video analysis."""
    video_path = args.video
    result = _execute("analyze-video", {"video": video_path}, orchestrator=orchestrator)
    print(result)
    return 0


def cmd_doctor(args, orchestrator: IRegistryServiceAggregate | None = None) -> int:
    """Check system dependencies and readiness."""
    result = _execute("doctor", {}, orchestrator=orchestrator)
    print(result)
    return 0
