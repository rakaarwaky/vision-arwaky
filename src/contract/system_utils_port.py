from abc import ABC, abstractmethod


class SystemUtilsPort(ABC):
    """Abstract port defining system utilities and helper functions."""

    @property
    @abstractmethod
    def FFMPEG_PATH(self):
        """Absolute path to the ffmpeg binary."""
        pass

    @property
    @abstractmethod
    def FFPROBE_PATH(self):
        """Absolute path to the ffprobe binary."""
        pass

    @abstractmethod
    def file_exists(self, path):
        """Check if file exists on disk."""
        pass

    @abstractmethod
    def get_file_size_mb(self, path):
        """Get file size in Megabytes."""
        pass

    @abstractmethod
    def validate_path(self, path):
        """Validate and return absolute expanded path, raising errors if invalid."""
        pass
