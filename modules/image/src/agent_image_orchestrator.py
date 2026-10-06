"""Image Agent Orchestrator — coordinates image processing and OCR via DI."""

from modules.shared.src.contract_image_processing_protocol import (
    IImageProcessingProtocol,
)
from modules.shared.src.contract_registry_service_aggregate import (
    IRegistryServiceAggregate,
)
from modules.shared.src.contract_tesseract_ocr_protocol import (
    ITesseractOCRProtocol,
)
from modules.shared.src.taxonomy_vision_error import (
    DependencyExecutionError,
    InvalidParameterError,
)
from modules.shared.src.taxonomy_vision_vo import (
    AnalysisPrompt,
    CommandName,
    CommandOutput,
    FilePath,
    LanguageCode,
    SystemCommandParams,
)
from modules.shared.src.utility_command_output import to_command_output


class ImageOrchestrator(IRegistryServiceAggregate):
    """Orchestrator for image processing domain (pure delegation facade)."""

    def __init__(
        self,
        image_processing: IImageProcessingProtocol,
        tesseract: ITesseractOCRProtocol,
    ):
        self._image_processing = image_processing
        self._tesseract = tesseract

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
            prompt = AnalysisPrompt(value=kwargs_dict.get("prompt"))
            return to_command_output(cap.analyze_screenshot(img, prompt))
        elif command.value == "ocr":
            img = FilePath.from_str(kwargs_dict["image"])
            lang = LanguageCode(value=kwargs_dict.get("lang") or "eng")
            try:
                return CommandOutput(
                    value=self._tesseract.extract_text(img, lang).value
                )
            except RuntimeError as e:
                raise DependencyExecutionError(str(e)) from e
        elif command.value == "compare":
            img1 = FilePath.from_str(kwargs_dict["image1"])
            img2 = FilePath.from_str(kwargs_dict["image2"])
            return to_command_output(cap.compare_screenshots(img1, img2))
        raise InvalidParameterError(f"Unknown image command: {command.value}")
