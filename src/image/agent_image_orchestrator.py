"""Image Agent Orchestrator — coordinates image processing capabilities."""

import importlib
import json
from typing import Any, Dict

from src.shared.vision_models_vo import FilePath, LanguageCode, AnalysisPrompt, BoundingBox


class ImageOrchestrator:
    """Orchestrator for image processing domain."""

    @staticmethod
    def get_opencv():
        module = importlib.import_module("src.opencv.infrastructure_opencv_image_adapter")
        cls = getattr(module, "OpenCVImageAdapter")
        return cls()

    @staticmethod
    def get_tesseract():
        module = importlib.import_module("src.image.infrastructure_tesseract_ocr_adapter")
        cls = getattr(module, "TesseractOCRAdapter")
        return cls()

    @staticmethod
    def get_llm():
        module = importlib.import_module("src.image.infrastructure_llm_vision_adapter")
        cls = getattr(module, "LLMVisionAdapter")
        return cls()

    @staticmethod
    def get_image_processing():
        cap_mod = importlib.import_module("src.image.capabilities_image_processing_processor")
        cap_cls = getattr(cap_mod, "ImageProcessingProcessor")
        return cap_cls(
            opencv_port=ImageOrchestrator.get_opencv(),
            tesseract_port=ImageOrchestrator.get_tesseract(),
            llm_port=ImageOrchestrator.get_llm(),
        )

    @staticmethod
    def execute_image_cmd(command: str, kwargs: Dict[str, Any]) -> str | None:
        """Execute image-related commands."""
        cap = ImageOrchestrator.get_image_processing()

        if command == "analyze":
            img = FilePath(value=kwargs["image"])
            prompt_val = kwargs.get("prompt")
            prompt = AnalysisPrompt(value=prompt_val)
            return json.dumps(cap.analyze_screenshot(img, prompt).model_dump(), indent=2)
        elif command == "ocr":
            img = FilePath(value=kwargs["image"])
            lang_val = kwargs.get("lang") or "eng"
            lang = LanguageCode(value=lang_val)
            return cap.extract_text(img, lang).value
        elif command == "elements":
            img = FilePath(value=kwargs["image"])
            return json.dumps([e.model_dump() for e in cap.find_elements(img)], indent=2)
        elif command == "compare":
            img1 = FilePath(value=kwargs["image1"])
            img2 = FilePath(value=kwargs["image2"])
            return json.dumps(cap.compare_screenshots(img1, img2), indent=2)
        return None
