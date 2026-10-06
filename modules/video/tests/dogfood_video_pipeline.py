"""Dogfood tests: video CLI against live service; skip if unavailable."""

import shutil
import subprocess

import pytest


class TestVideoDogfood:
    def test_cli_available(self):
        cli = shutil.which("vision-arwaky-cli")
        if cli is None:
            pytest.skip("vision-arwaky-cli binary not installed; dogfood skipped")
        result = subprocess.run(
            [cli, "--help"], capture_output=True, text=True, timeout=30, check=False
        )
        assert result.returncode == 0

    def test_video_info_pipeline(self, tmp_path):
        ffmpeg = shutil.which("ffmpeg")
        if ffmpeg is None or shutil.which("vision-arwaky-cli") is None:
            pytest.skip("ffmpeg or vision-arwaky-cli not installed; dogfood skipped")
        vid = tmp_path / "dogfood.mp4"
        if not vid.exists():
            pytest.skip("no live video fixture available; dogfood skipped")
        result = subprocess.run(
            ["vision-arwaky-cli", "video-info", str(vid)],
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
        assert result.returncode == 0
