"""Tests for CLI and MCP surfaces."""

import json
from pathlib import Path


class TestCLIHandler:
    def test_create_parser(self):
        from modules.cli.src.surface_cli_controller import create_parser

        parser = create_parser()
        assert parser is not None
        assert parser.prog == "vision"

    def test_parser_image_commands(self):
        from modules.cli.src.surface_cli_controller import create_parser

        parser = create_parser()
        for cmd in ["analyze", "ocr", "elements", "compare"]:
            sub = parser._subparsers._group_actions[0].choices.get(cmd)
            assert sub is not None, f"Missing command: {cmd}"

    def test_parser_video_commands(self):
        from modules.cli.src.surface_cli_controller import create_parser

        parser = create_parser()
        for cmd in [
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
        ]:
            sub = parser._subparsers._group_actions[0].choices.get(cmd)
            assert sub is not None, f"Missing command: {cmd}"

    def test_parser_test_command(self):
        from modules.cli.src.surface_cli_controller import create_parser

        parser = create_parser()
        sub = parser._subparsers._group_actions[0].choices.get("test")
        assert sub is not None


class TestMCPHandler:
    def test_check_dependencies(self):
        import shutil

        from modules.mcp.src.surface_mcp_controller import _check_dependencies

        deps = _check_dependencies(shutil)
        assert isinstance(deps, dict)
        assert "opencv" in deps
        assert "pytesseract" in deps
        assert "ffmpeg" in deps

    def test_public_config_contains_no_credentials(self):
        config_text = (Path(__file__).parents[1] / "config.yaml").read_text()
        assert "api_key:" not in config_text
        assert "sk-" not in config_text

    def test_list_commands(self):
        from modules.mcp.src.surface_mcp_action import vision_list_commands

        result = vision_list_commands()
        data = json.loads(result)
        assert "image" in data
        assert "video" in data
        assert "analyze-video" in {item["command"] for item in data["video"]}
        assert "memory" not in data

    def test_list_commands_image(self):
        from modules.mcp.src.surface_mcp_action import vision_list_commands

        result = vision_list_commands(domain="image")
        data = json.loads(result)
        assert len(data) == 4

    def test_help_all(self):
        from modules.mcp.src.surface_mcp_action import vision_help

        result = vision_help()
        assert len(result) > 100

    def test_help_video_section(self):
        from modules.mcp.src.surface_mcp_action import vision_help

        result = vision_help(section="video")
        assert "analyze-video" in result
        assert result.startswith("## CLI reference: video")

    def test_status_uses_runtime_endpoint_and_package_version(self, monkeypatch):
        from modules.mcp.src import surface_mcp_action

        calls = []

        class Response:
            status_code = 200

        def fake_get(url, headers, timeout):
            calls.append((url, headers, timeout))
            return Response()

        monkeypatch.setenv("LLAMA_API_URL", "https://status.example/v1")
        monkeypatch.setenv("LLAMA_API_KEY", "test-key")
        monkeypatch.setenv("LLAMA_MODEL", "test-vision-model")
        monkeypatch.setattr(surface_mcp_action.requests, "get", fake_get)

        result = json.loads(surface_mcp_action.vision_status())

        assert result["configuration"]["llm_endpoint"] == "https://status.example/v1"
        assert result["configuration"]["llm_model"] == "test-vision-model"
        assert result["configuration"]["llm_api_key_configured"] is True
        assert result["dependencies"]["llm_endpoint"] == "OK"
        assert result["capabilities"]["llm_vision"] is True
        assert result["server"].endswith("v2.0.7")
        assert calls == [
            (
                "https://status.example/v1/models",
                {"Authorization": "Bearer test-key"},
                5,
            )
        ]

    def test_cancel_empty(self):
        from modules.mcp.src.surface_mcp_action import vision_cancel

        result = json.loads(vision_cancel())
        assert result["active_jobs"] == 0
        assert result["supported"] is False

    def test_cancel_unknown(self):
        from modules.mcp.src.surface_mcp_action import vision_cancel

        result = json.loads(vision_cancel(job_id="invalid"))
        assert "error" in result
        assert result["supported"] is False


class TestMCPExecute:
    def test_execute_analyze_no_image(self):
        from modules.mcp.src.surface_mcp_action import vision_execute

        result = json.loads(vision_execute(command="analyze"))
        assert "error" in result

    def test_execute_unknown_command(self):
        from modules.mcp.src.surface_mcp_action import vision_execute

        result = json.loads(vision_execute(command="nonexistent"))
        assert "error" in result

    def test_execute_ocr_no_image(self):
        from modules.mcp.src.surface_mcp_action import vision_execute

        result = json.loads(vision_execute(command="ocr"))
        assert "error" in result

    def test_execute_elements_no_image(self):
        from modules.mcp.src.surface_mcp_action import vision_execute

        result = json.loads(vision_execute(command="elements"))
        assert "error" in result


class TestCLIEntry:
    def test_entry_module_imports(self):
        from modules import root_cli_entry

        assert callable(root_cli_entry.cli)

    def test_mcp_entry_module_imports(self):
        from modules import root_mcp_entry

        assert callable(root_mcp_entry.main)

    def test_tui_entry_module_imports(self):
        from modules import root_tui_entry

        assert callable(root_tui_entry.main)


class TestTracking:
    def test_tracking_import(self):
        from modules.opencv.src.capabilities_opencv_image_adapter import (
            OpenCVImageAdapter,
        )
        from modules.video.src.capabilities_object_tracker import ObjectTrackingTracker

        tracker = ObjectTrackingTracker(OpenCVImageAdapter())
        assert tracker is not None
