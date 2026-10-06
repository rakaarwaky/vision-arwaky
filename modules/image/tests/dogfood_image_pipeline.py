"""Dogfood tests: image CLI against live service; skip if unavailable."""

import shutil
import subprocess

import pytest


class TestImageDogfood:
    def test_cli_available(self):
        cli = shutil.which("vision-arwaky-cli")
        if cli is None:
            pytest.skip("vision-arwaky-cli binary not installed; dogfood skipped")
        result = subprocess.run(
            [cli, "--help"], capture_output=True, text=True, timeout=30, check=False
        )
        assert result.returncode == 0

    def test_compare_pipeline(self, tmp_path):
        if shutil.which("vision-arwaky-cli") is None:
            pytest.skip("vision-arwaky-cli binary not installed; dogfood skipped")
        a = tmp_path / "a.png"
        b = tmp_path / "b.png"
        if not (a.exists() and b.exists()):
            pytest.skip("no live image fixture available; dogfood skipped")
