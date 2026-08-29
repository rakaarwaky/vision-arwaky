"""Unit tests for CLI parser and MCP surface handlers."""

import json
from pathlib import Path

from modules.cli.src.surface_cli_controller import create_parser
from modules.mcp.src import surface_mcp_action
from modules.mcp.src.surface_mcp_action import (
    vision_execute,
    vision_help,
    vision_list_commands,
    vision_status,
)


class TestCLIParsing:
    def test_parser_registers_all_clean_commands(self):
        parser = create_parser()
        expected_image = {"analyze", "ocr", "compare"}
        expected_video = {
            "video-info",
            "extract-frames",
            "check-corruption",
            "detect-scenes",
            "detect-motion",
            "track",
            "analyze-video",
        }
        choices = parser._subparsers._group_actions[0].choices
        for cmd in expected_image | expected_video:
            assert cmd in choices, f"Missing command in parser: {cmd}"

    def test_parser_excludes_bloat_commands(self):
        parser = create_parser()
        choices = parser._subparsers._group_actions[0].choices
        for cmd in ["elements", "convert", "create-gif", "timeline", "test"]:
            assert cmd not in choices, f"Bloat command still in parser: {cmd}"


class TestMCPSurface:
    def test_list_commands_schema(self):
        result = json.loads(vision_list_commands())
        assert "image" in result
        assert "video" in result
        image_cmds = {item["command"] for item in result["image"]}
        video_cmds = {item["command"] for item in result["video"]}
        assert image_cmds == {"analyze", "ocr", "compare"}
        assert "analyze-video" in video_cmds
        assert "convert" not in video_cmds
        assert "elements" not in image_cmds

    def test_list_commands_domain_filter(self):
        result = json.loads(vision_list_commands(domain="image"))
        assert isinstance(result, list)
        assert len(result) == 3

    def test_help_output(self):
        help_all = vision_help()
        assert len(help_all) > 100
        help_video = vision_help(section="video")
        assert "analyze-video" in help_video

    def test_status_endpoint(self, monkeypatch):
        class FakeResponse:
            status_code = 200
            def json(self):
                return {"data": [{"id": "local-vlm"}]}

        monkeypatch.setenv("LLAMA_API_URL", "https://status.example/v1")
        monkeypatch.setenv("LLAMA_API_KEY", "test-key")
        monkeypatch.setattr(surface_mcp_action.requests, "get", lambda *a, **kw: FakeResponse())

        status = json.loads(vision_status())
        assert status["configuration"]["llm_endpoint"] == "https://status.example/v1"
        assert status["dependencies"]["llm_endpoint"] == "OK"

    def test_execute_validation_errors(self):
        # Missing required parameter returns error JSON without crash
        res_analyze = json.loads(vision_execute(command="analyze"))
        assert "error" in res_analyze

        res_unknown = json.loads(vision_execute(command="nonexistent_cmd"))
        assert "error" in res_unknown
