"""Image processing capability executing LLM-based screenshot analysis."""

from modules.shared.src.image.contract_image_processing_protocol import (
    IImageProcessingProtocol,
)
from modules.shared.src.image.contract_llm_vision_protocol import ILLMVisionProtocol
from modules.shared.src.taxonomy_vision_vo import (
    AnalysisPrompt,
    FilePath,
    VisionAnalysis,
)


class ImageProcessingProcessor(IImageProcessingProtocol):
    """Image processing capability executing LLM-based analysis only."""

    def __init__(
        self,
        llm_port: ILLMVisionProtocol | None = None,
    ):
        self._llm = llm_port

    def analyze_screenshot(
        self, image_path: FilePath, prompt: AnalysisPrompt | None = None
    ) -> VisionAnalysis:
        """Analyze screenshot with LLM (defaults to image description)."""
        if self._llm is not None:
            try:
                p_val = prompt.value if prompt and prompt.value else None
                analysis = self._llm.analyze_image(
                    image_path, AnalysisPrompt(value=p_val or "Describe this image.")
                )
                return VisionAnalysis(
                    source="llm",
                    text=analysis,
                    model=self._llm.model.value,
                )
            except (RuntimeError, ValueError, OSError, ImportError) as e:
                return VisionAnalysis(
                    source="opencv",
                    text=str(e),
                    error=str(e),
                )

        return VisionAnalysis(
            source="opencv",
            text="No VLM available",
        )

    def __repr__(self) -> str:
        return "ImageProcessingProcessor()"
