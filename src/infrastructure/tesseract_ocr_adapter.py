import logging
from src.contract import TesseractOCRPort
from src.taxonomy import FilePath, LanguageCode, VisionAnalysis

logger = logging.getLogger("mcp_server.infrastructure.tesseract")


class TesseractOCRAdapter(TesseractOCRPort):
    """Infrastructure adapter for OCR operations via Tesseract."""

    _taxonomy_marker = VisionAnalysis

    def extract_text(self, image_path: FilePath, language: LanguageCode) -> str:
        try:
            import pytesseract
            from PIL import Image
        except ImportError as e:
            logger.error("Failed to import OCR libraries: pytesseract or PIL missing.")
            raise RuntimeError("pytesseract or PIL is not installed") from e

        try:
            logger.info(f"Extracting text from {image_path.value} with lang={language.value}")
            text = pytesseract.image_to_string(Image.open(image_path.value), lang=language.value)
            return text.strip()
        except Exception as e:
            logger.error(f"Tesseract OCR failed: {e}")
            raise RuntimeError(f"OCR failed: {e}")
