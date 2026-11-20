"""Video Agent Orchestrator — coordinates video understanding via DI."""

from modules.shared.src.common.taxonomy_vision_error import (
    InvalidParameterError,
)
from modules.shared.src.common.taxonomy_vision_vo import (
    AnalysisPrompt,
    CommandName,
    CommandOutput,
    FilePath,
    SystemCommandParams,
)
from modules.shared.src.common.utility_command_output import (
    to_command_output,
)
from modules.shared.src.contract_registry_service_aggregate import (
    IRegistryServiceAggregate,
)
from modules.shared.src.video.contract_video_understanding_protocol import (
    IVideoUnderstandingProtocol,
)


class VideoOrchestrator(IRegistryServiceAggregate):
    """Orchestrator for video processing domain (pure delegation facade)."""

    def __init__(
        self,
        video_understanding: IVideoUnderstandingProtocol | None = None,
    ):
        self._video_understanding = video_understanding

    def execute_in_process(
        self,
        command: CommandName,
        kwargs: dict | SystemCommandParams,
    ) -> CommandOutput:
        """Execute video-related commands by delegating to injected capabilities."""
        kw = kwargs if isinstance(kwargs, dict) else kwargs.model_dump()
        if command.value == "analyze-video":
            if self._video_understanding is None:
                raise InvalidParameterError(
                    "Video understanding capability is not configured for analyze-video"
                )
            vid = FilePath.from_str(kw["video"])
            prompt = AnalysisPrompt(value=kw.get("prompt", ""))
            result = self._video_understanding.analyze(
                vid,
                prompt,
            )
            return to_command_output(result)
        raise InvalidParameterError(f"Unknown video command: {command.value}")
