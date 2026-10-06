"""Dogfood tests: system CLI against live service; skip if unavailable."""

import shutil
import subprocess

import pytest


class TestSystemDogfood:
    def test_cli_available(self):
        cli = shutil.which("vision-arwaky-cli")
        if cli is None:
            pytest.skip("vision-arwaky-cli binary not installed; dogfood skipped")
        result = subprocess.run(
            [cli, "--help"], capture_output=True, text=True, timeout=30, check=False
        )
        assert result.returncode == 0

    def test_status_pipeline(self):
        if shutil.which("vision-arwaky-cli") is None:
            pytest.skip("vision-arwaky-cli binary not installed; dogfood skipped")
        # The CLI parser only accepts system commands exposed as subcommands;
        # "init" is the live system-domain pipeline (status has no CLI subcommand).
        result = subprocess.run(
            ["vision-arwaky-cli", "init", "."],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        assert result.returncode == 0
