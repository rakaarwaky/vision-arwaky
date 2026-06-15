from abc import ABC, abstractmethod


class LLMVisionPort(ABC):
    """Abstract port for local VLM image analysis capabilities."""

    @property
    @abstractmethod
    def backend(self):
        """The active backend type: native or external."""
        pass

    @property
    @abstractmethod
    def model(self):
        """The active model name."""
        pass

    @abstractmethod
    def analyze_image(self, image_path, prompt, timeout = 120):
        """Analyze image with custom prompt using the VLM."""
        pass
