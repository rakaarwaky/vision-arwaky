"""Dogfood tests: video CLI against live session; skip if unavailable."""

import subprocess
import sys


class TestVideoDogfood:
    def test_video_cli_help(self):
        """Verify the video CLI help command runs without error."""
        result = subprocess.run(
            [sys.executable, "-m", "modules.cli.src.surface_cli_controller", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0
