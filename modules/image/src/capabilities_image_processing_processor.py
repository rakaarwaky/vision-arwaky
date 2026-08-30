from modules.shared.src.contract_image_processing_protocol import (
    ImageProcessingProtocol,
)
from modules.shared.src.contract_llm_vision_protocol import LLMVisionProtocol
from modules.shared.src.contract_tesseract_ocr_protocol import (
    TesseractOCRProtocol,
)
from modules.shared.src.taxonomy_vision_constant import (
    DEFAULT_OCR_LANGUAGE,
    IMAGE_DIFF_THRESHOLD,
    IMAGE_MAX_PIXEL_VALUE,
    MIN_DIFF_CONTOUR_AREA,
)
from modules.shared.src.taxonomy_vision_vo import (
    AnalysisPrompt,
    BoundingBox,
    FilePath,
    LanguageCode,
    OcrText,
    ScreenshotComparison,
    VisionAnalysis,
)
from modules.shared.src.utility_opencv_ops import (
    apply_threshold,
    compute_abs_diff,
    compute_phash,
    find_contours,
    get_bounding_box,
    get_contour_area,
    pad_image_border,
    read_image,
    resize_image,
    to_grayscale,
)


class ImageProcessingProcessor(ImageProcessingProtocol):
    """Image processing capability executing screenshot analysis and comparisons."""

    def __init__(
        self,
        tesseract_port: TesseractOCRProtocol,
        llm_port: LLMVisionProtocol,
    ):
        self._tesseract = tesseract_port
        self._llm = llm_port

    def analyze_screenshot(
        self, image_path: FilePath, prompt: AnalysisPrompt
    ) -> VisionAnalysis:
        """Analyze screenshot for text and visual content.

        If prompt is provided and a local VLM is available, use LLM for
        open-ended visual analysis. Otherwise fallback to OCR text extraction.
        """
        p_val = prompt.value if prompt else None
        if p_val:
            try:
                analysis = self._llm.analyze_image(
                    image_path, AnalysisPrompt(value=p_val)
                )
                return VisionAnalysis(
                    source="llm",
                    text=analysis,
                    model=self._llm.model.value,
                )
            except (
                RuntimeError,
                ValueError,
                OSError,
                ImportError,
            ) as e:
                # Fallback to OCR if LLM fails
                return VisionAnalysis(
                    source="opencv",
                    text=self.extract_text(
                        image_path, LanguageCode(value=DEFAULT_OCR_LANGUAGE)
                    ).value,
                    error=str(e),
                )

        # Default: OCR text extraction
        text = self.extract_text(
            image_path, LanguageCode(value=DEFAULT_OCR_LANGUAGE)
        ).value
        return VisionAnalysis(
            source="opencv",
            text=text,
        )

    def extract_text(self, image_path: FilePath, lang: LanguageCode) -> OcrText:
        """Extract text from image using OCR."""
        return self._tesseract.extract_text(image_path, lang)

    def compare_screenshots(
        self, image_path1: FilePath, image_path2: FilePath
    ) -> ScreenshotComparison:
        """Compare two screenshots and find differences."""
        img1 = read_image(image_path1)
        img2 = read_image(image_path2)

        if img1 is None or img2 is None:
            raise ValueError("Failed to load one or both images")

        if img1.shape != img2.shape:
            h1, w1 = img1.shape[:2]
            h2, w2 = img2.shape[:2]
            scale = min(w1 / w2, h1 / h2)
            new_w, new_h = int(w2 * scale), int(h2 * scale)
            img2 = resize_image(img2, new_w, new_h)
            # Center-pad if needed
            if new_w < w1 or new_h < h1:
                img2 = pad_image_border(
                    img2,
                    top=0,
                    bottom=h1 - new_h,
                    left=0,
                    right=w1 - new_w,
                )

        diff = compute_abs_diff(img1, img2)
        gray_diff = to_grayscale(diff)

        thresh = apply_threshold(gray_diff, IMAGE_DIFF_THRESHOLD, IMAGE_MAX_PIXEL_VALUE)
        contours = find_contours(thresh)

        differences: list[BoundingBox] = []
        for cnt in contours:
            area = get_contour_area(cnt)
            if area > MIN_DIFF_CONTOUR_AREA:
                differences.append(get_bounding_box(cnt))

        hash1 = compute_phash(img1)
        hash2 = compute_phash(img2)

        return ScreenshotComparison(
            identical=len(differences) == 0 and hash1 == hash2,
            phash_diff=hash1 != hash2,
            differences=differences,
        )
