from abc import ABC, abstractmethod
from src.taxonomy import FilePath, LanguageCode


class TesseractOCRPort(ABC):
    """Abstract port for OCR text extraction services."""

    @abstractmethod
    def extract_text(self, image_path: FilePath, language: LanguageCode):
        """Extract text from image at image_path using OCR."""
        pass
