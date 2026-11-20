"""Image Agent Orchestrator — coordinates image processing via DI."""

from modules.shared.src.contract_registry_service_aggregate import (
    IRegistryServiceAggregate,
)
from modules.shared.src.image.contract_image_processing_protocol import (
    IImageProcessingProtocol,
)
from modules.shared.src.taxonomy_vision_error import (
    InvalidParameterError,
)
from modules.shared.src.taxonomy_vision_vo import (
    AnalysisPrompt,
    CommandName,
    CommandOutput,
    FilePath,
    SystemCommandParams,
)
from modules.shared.src.utility_command_output import to_command_output


class ImageOrchestrator(IRegistryServiceAggregate):
    """Orchestrator for image processing domain (pure delegation facade)."""

    def __init__(
        self,
        image_processing: IImageProcessingProtocol,
    ):
        self._image_processing = image_processing

    def execute_in_process(
        self,
        command: CommandName,
        kwargs: dict | SystemCommandParams,
    ) -> CommandOutput:
        """Execute image-related commands by delegating to injected ports."""
        cap = self._image_processing
        kwargs_dict = kwargs if isinstance(kwargs, dict) else kwargs.model_dump()

        if command.value == "analyze":
            img = FilePath.from_str(kwargs_dict["image"])
            prompt = AnalysisPrompt(value=kwargs_dict.get("prompt") or "")
            return to_command_output(cap.analyze_screenshot(img, prompt))
        raise InvalidParameterError(f"Unknown image command: {command.value}")
