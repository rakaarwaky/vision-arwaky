"""Image Agent Orchestrator — coordinates image processing capabilities via DI."""

import json
from typing import Any

from modules.shared.src.contract_image_processing_protocol import (
    ImageProcessingProtocol,
)
from modules.shared.src.contract_llm_vision_protocol import LLMVisionProtocol
from modules.shared.src.contract_registry_service_aggregate import (
    RegistryServiceAggregate,
)
from modules.shared.src.contract_tesseract_ocr_protocol import (
    TesseractOCRProtocol,
)
from modules.shared.src.taxonomy_vision_models_vo import (
    AnalysisPrompt,
    CommandName,
    CommandOutput,
    FilePath,
    LanguageCode,
)


class ImageOrchestrator(RegistryServiceAggregate):
    """Orchestrator for image processing domain (pure delegation facade)."""

    def __init__(
        self,
        image_processing: ImageProcessingProtocol,
        tesseract: TesseractOCRProtocol,
        llm: LLMVisionProtocol,
    ):
        self._image_processing = image_processing
        self._tesseract = tesseract
        self._llm = llm


    def execute_in_process(
        self,
        command: CommandName,
        kwargs: dict[str, Any],
    ) -> CommandOutput:
        """Execute image-related commands by delegating to the injected processor."""
        cap = self._image_processing

        if command.value == "analyze":
            img = FilePath(value=kwargs["image"])
            prompt_val = kwargs.get("prompt")
            prompt = AnalysisPrompt(value=prompt_val)
            return CommandOutput(
                value=json.dumps(
                    cap.analyze_screenshot(img, prompt).model_dump(), indent=2
                )
            )
        elif command.value == "ocr":
            img = FilePath(value=kwargs["image"])
            lang_val = kwargs.get("lang") or "eng"
            lang = LanguageCode(value=lang_val)
            return CommandOutput(value=cap.extract_text(img, lang).value)
        elif command.value == "compare":
            img1 = FilePath(value=kwargs["image1"])
            img2 = FilePath(value=kwargs["image2"])
            return CommandOutput(
                value=json.dumps(
                    cap.compare_screenshots(img1, img2).model_dump(), indent=2
                )
            )
        raise ValueError(f"Unknown image command: {command.value}")

