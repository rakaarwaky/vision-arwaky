"""Dogfood tests: image CLI against live session; skip if unavailable."""

import subprocess
import sys


class TestImageDogfood:
    def test_image_cli_help(self):
        """Verify the image CLI help command runs without error."""
        result = subprocess.run(
            [sys.executable, "-m", "modules.cli.src.surface_cli_controller", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0
