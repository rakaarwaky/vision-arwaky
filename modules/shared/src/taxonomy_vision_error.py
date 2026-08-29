"""Domain and infrastructure error types for the vision system."""

from __future__ import annotations


class VisionDomainError(Exception):
    """Base exception for all vision domain and operation errors."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class ImageProcessingError(VisionDomainError):
    """Raised when an image operation fails or inputs are unreadable."""


class VideoProcessingError(VisionDomainError):
    """Raised when a video operation fails or media is corrupt."""


class InvalidParameterError(VisionDomainError):
    """Raised when an operation receives invalid domain arguments."""


class DependencyExecutionError(VisionDomainError):
    """Raised when an external tool (FFmpeg, Tesseract, VLM) fails."""
