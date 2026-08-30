"""Unit tests for MCP surface handlers."""

import json

from modules.mcp.src.surface_mcp_command import (
    vision_execute,
    vision_help,
    vision_list_commands,
    vision_status,
)


class TestMCPSurface:
    def test_list_commands_schema(self):
        result = json.loads(vision_list_commands())
        assert "workspace" in result
        assert "image" in result
        assert "video" in result
        workspace_cmds = {item["command"] for item in result["workspace"]}
        image_cmds = {item["command"] for item in result["image"]}
        video_cmds = {item["command"] for item in result["video"]}
        assert workspace_cmds == {"init"}
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
        import requests

        monkeypatch.setattr(requests, "get", lambda *a, **kw: FakeResponse())

        status = json.loads(vision_status())
        assert status["configuration"]["llm_endpoint"] == "https://status.example/v1"
        assert status["dependencies"]["llm_endpoint"] == "OK"

    def test_execute_validation_errors(self):
        res_analyze = json.loads(vision_execute(command="analyze"))
        assert "error" in res_analyze

        res_unknown = json.loads(vision_execute(command="nonexistent_cmd"))
        assert "error" in res_unknown
