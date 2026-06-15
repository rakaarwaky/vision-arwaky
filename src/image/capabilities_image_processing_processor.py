from typing import Dict, Any, List
from src.shared.image_processing_protocol import ImageProcessingProtocol
from src.shared.opencv_image_port import OpenCVImagePort
from src.shared.tesseract_ocr_port import TesseractOCRPort
from src.shared.llm_vision_port import LLMVisionPort
from src.shared.vision_models_vo import BoundingBox, Detection, VisionAnalysis, FilePath, LanguageCode, AnalysisPrompt, OcrText


class ImageProcessingProcessor(ImageProcessingProtocol):
    """Image processing capability executing screenshot analysis and comparisons."""

    def __init__(
        self,
        opencv_port: OpenCVImagePort,
        tesseract_port: TesseractOCRPort,
        llm_port: LLMVisionPort,
    ):
        self._opencv = opencv_port
        self._tesseract = tesseract_port
        self._llm = llm_port

    def analyze_screenshot(self, image_path: FilePath, prompt: AnalysisPrompt) -> VisionAnalysis:
        """Analyze screenshot for UI elements and text.
        
        If prompt is provided and a local VLM is available, use LLM for 
        open-ended visual analysis. Otherwise fallback to OCR + element detection.
        """
        p_val = prompt.value if prompt else None
        if p_val:
            try:
                analysis = self._llm.analyze_image(image_path.value, p_val)
                return VisionAnalysis(
                    source="llm",
                    text=analysis,
                    model=self._llm.model or "unknown",
                )
            except Exception as e:
                # Fallback to OpenCV if LLM fails
                return VisionAnalysis(
                    source="opencv",
                    text=self.extract_text(image_path, LanguageCode(value="eng")).value,
                    elements=self.find_elements(image_path),
                    error=str(e),
                )
        
        # Default: OCR + element detection
        text = self.extract_text(image_path, LanguageCode(value="eng")).value
        elements = self.find_elements(image_path)
        return VisionAnalysis(
            source="opencv",
            text=text,
            elements=elements,
        )

    def extract_text(self, image_path: FilePath, lang: LanguageCode) -> OcrText:
        """Extract text from image using OCR."""
        text_str = self._tesseract.extract_text(image_path, lang)
        return OcrText(value=text_str)

    def find_elements(self, image_path: FilePath) -> List[Detection]:
        """Find UI elements (buttons, input fields, etc)."""
        image = self._opencv.read_image(image_path)
        if image is None:
            raise ValueError(f"Failed to load image: {image_path.value}")

        gray = self._opencv.to_grayscale(image)
        edges = self._opencv.detect_edges(gray, 50, 150)
        contours = self._opencv.find_contours(edges)

        detections = []
        for cnt in contours:
            area = self._opencv.get_contour_area(cnt)
            if area > 100:  # Filter out noise
                x, y, w, h = self._opencv.get_bounding_box(cnt)
                detections.append(
                    Detection(
                        label="ui_element",
                        confidence=1.0,
                        bbox=BoundingBox(x=x, y=y, width=w, height=h),
                    )
                )
        return detections

    def compare_screenshots(self, image_path1: FilePath, image_path2: FilePath) -> Dict[str, Any]:
        """Compare two screenshots and find differences."""
        img1 = self._opencv.read_image(image_path1)
        img2 = self._opencv.read_image(image_path2)

        if img1 is None or img2 is None:
            raise ValueError("Failed to load one or both images")

        if img1.shape != img2.shape:
            img2 = self._opencv.cv2.resize(img2, (img1.shape[1], img1.shape[0]))

        diff = self._opencv.abs_diff(img1, img2)
        gray_diff = self._opencv.to_grayscale(diff)

        _, thresh = self._opencv.cv2.threshold(
            gray_diff, 30, 255, self._opencv.cv2.THRESH_BINARY
        )
        contours = self._opencv.find_contours(thresh)

        differences = []
        for cnt in contours:
            area = self._opencv.get_contour_area(cnt)
            if area > 50:
                x, y, w, h = self._opencv.get_bounding_box(cnt)
                differences.append(
                    BoundingBox(x=x, y=y, width=w, height=h).model_dump()
                )

        hash1 = self._opencv.compute_phash(img1)
        hash2 = self._opencv.compute_phash(img2)

        return {
            "identical": len(differences) == 0 and hash1 == hash2,
            "phash_diff": hash1 != hash2,
            "differences": differences,
        }
