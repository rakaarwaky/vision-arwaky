from abc import ABC, abstractmethod

from modules.shared.src.taxonomy_vision_vo import FilePath, LanguageCode, OcrText


class TesseractOCRProtocol(ABC):
    """Abstract port for OCR text extraction services."""

    @abstractmethod
    def extract_text(self, image_path: FilePath, language: LanguageCode) -> OcrText:
        """Extract text from image at image_path using OCR."""
