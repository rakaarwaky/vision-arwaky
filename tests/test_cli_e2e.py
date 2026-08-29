"""End-to-end tests for the packaged Vision Arwaky CLI."""

import json
import os
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

CLI_COMMANDS = [
    "analyze",
    "ocr",
    "elements",
    "compare",
    "video-info",
    "extract-frames",
    "convert",
    "check-corruption",
    "create-gif",
    "detect-scenes",
    "detect-motion",
    "track",
    "timeline",
    "analyze-video",
    "test",
]


def _run_cli(
    *args: str, env: dict[str, str], timeout: int = 30
) -> subprocess.CompletedProcess[str]:
    """Run one CLI command without shell evaluation and capture its output."""
    return subprocess.run(
        [sys.executable, "-m", "modules.root_cli_entry", *args],
        cwd=Path(__file__).parents[1],
        env=env,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


def _make_fixture(tmp_path: Path) -> tuple[Path, Path]:
    """Create a small OCR image and moving-object video for CLI E2E tests."""
    image_path = tmp_path / "sample.png"
    image = np.zeros((240, 320, 3), dtype=np.uint8)
    image[:] = (255, 255, 255)
    cv2.rectangle(image, (30, 30), (290, 210), (255, 0, 0), 3)
    cv2.putText(
        image,
        "E2E TEST",
        (55, 125),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.2,
        (0, 0, 0),
        2,
    )
    assert cv2.imwrite(str(image_path), image)

    video_path = tmp_path / "sample.mp4"
    writer = cv2.VideoWriter(
        str(video_path), cv2.VideoWriter_fourcc(*"mp4v"), 10, (160, 120)
    )
    assert writer.isOpened()
    for index in range(20):
        frame = np.zeros((120, 160, 3), dtype=np.uint8)
        frame[:] = (30, 30, 100) if index < 10 else (100, 30, 30)
        x = 10 + (index * 5) % 100
        cv2.rectangle(frame, (x, 35), (x + 30, 65), (0, 255, 0), -1)
        writer.write(frame)
    writer.release()
    return image_path, video_path


def _test_environment() -> dict[str, str]:
    """Return a deterministic environment with an unavailable local VLM endpoint."""
    env = os.environ.copy()
    env["LLAMA_API_URL"] = "http://127.0.0.1:1/v1"
    env.pop("LLAMA_API_KEY", None)
    return env


def test_every_cli_help_command_runs(tmp_path: Path) -> None:
    """Verify that every registered CLI command exposes a successful help screen."""
    del tmp_path
    env = _test_environment()
    for command in CLI_COMMANDS:
        result = _run_cli(command, "--help", env=env)
        assert result.returncode == 0, f"{command}: {result.stderr}"
        assert "usage:" in result.stdout.lower()


def test_deterministic_cli_workflows_run_end_to_end(tmp_path: Path) -> None:
    """Verify image and video commands complete with generated local fixtures."""
    image_path, video_path = _make_fixture(tmp_path)
    image2_path = tmp_path / "sample-copy.png"
    image2_path.write_bytes(image_path.read_bytes())
    converted_path = tmp_path / "converted.mp4"
    gif_path = tmp_path / "sample.gif"
    env = _test_environment()

    commands = [
        ("ocr", "--image", str(image_path)),
        ("elements", "--image", str(image_path)),
        (
            "compare",
            "--image1",
            str(image_path),
            "--image2",
            str(image2_path),
        ),
        ("video-info", "--video", str(video_path)),
        ("extract-frames", "--video", str(video_path), "--interval", "0.5"),
        (
            "convert",
            "--input",
            str(video_path),
            "--output",
            str(converted_path),
        ),
        ("check-corruption", "--video", str(video_path)),
        (
            "create-gif",
            "--video",
            str(video_path),
            "--output",
            str(gif_path),
            "--start",
            "0",
            "--duration",
            "1",
        ),
        ("detect-scenes", "--video", str(video_path), "--threshold", "20"),
        ("detect-motion", "--video", str(video_path), "--min-area", "20"),
        (
            "track",
            "--video",
            str(video_path),
            "--bbox",
            "10,35,30,30",
            "--max-frames",
            "10",
        ),
        ("timeline", "--video", str(video_path), "--interval", "1"),
    ]

    for command in commands:
        result = _run_cli(*command, env=env)
        assert result.returncode == 0, f"{command[0]}: {result.stderr}"
        assert result.stdout.strip(), command[0]

    assert converted_path.exists()
    assert gif_path.exists()

    corruption = _run_cli("check-corruption", "--video", str(video_path), env=env)
    assert json.loads(corruption.stdout)["corrupted"] is False


def test_vlm_cli_workflows_fail_soft_when_endpoint_unavailable(tmp_path: Path) -> None:
    """Verify image and smart-video commands return controlled fallback output."""
    image_path, video_path = _make_fixture(tmp_path)
    env = _test_environment()

    image_result = _run_cli(
        "analyze",
        "--image",
        str(image_path),
        "--prompt",
        "Describe this fixture",
        env=env,
    )
    assert image_result.returncode == 0, image_result.stderr
    assert image_result.stdout.strip()

    video_result = _run_cli(
        "analyze-video",
        "--video",
        str(video_path),
        "--interval",
        "10",
        "--min-area",
        "20",
        env=env,
    )
    assert video_result.returncode == 0, video_result.stderr
    payload = json.loads(video_result.stdout)
    assert payload["summary"]
    sampling = payload["sampling"]
    assert sampling["key_frames_extracted"] <= sampling["max_key_frames"] == 120
