
"""Tests for CLI and MCP surfaces."""
import json
import pytest


class TestCLIHandler:
    def test_create_parser(self):
        from src.cli.surface_cli_handler import create_parser
        parser = create_parser()
        assert parser is not None
        assert parser.prog == "vision"

    def test_parser_image_commands(self):
        from src.cli.surface_cli_handler import create_parser
        parser = create_parser()
        for cmd in ["analyze", "ocr", "elements", "compare"]:
            sub = parser._subparsers._group_actions[0].choices.get(cmd)
            assert sub is not None, f"Missing command: {cmd}"

    def test_parser_video_commands(self):
        from src.cli.surface_cli_handler import create_parser
        parser = create_parser()
        for cmd in ["video-info", "extract-frames", "convert", "check-corruption",
                     "create-gif", "detect-scenes", "detect-motion", "track", "timeline"]:
            sub = parser._subparsers._group_actions[0].choices.get(cmd)
            assert sub is not None, f"Missing command: {cmd}"

    def test_parser_test_command(self):
        from src.cli.surface_cli_handler import create_parser
        parser = create_parser()
        sub = parser._subparsers._group_actions[0].choices.get("test")
        assert sub is not None

    def test_parser_memory_subcommands(self):
        from src.cli.surface_cli_handler import create_parser
        parser = create_parser()
        mem = parser._subparsers._group_actions[0].choices.get("memory")
        assert mem is not None
        mem_sub = mem._subparsers._group_actions[0].choices
        for sc in ["store", "search", "list"]:
            assert sc in mem_sub, f"Missing memory subcommand: {sc}"


class TestMCPHandler:
    def test_check_dependencies(self):
        import shutil
        from src.mcp.surface_mcp_handler import _check_dependencies
        deps = _check_dependencies(shutil)
        assert isinstance(deps, dict)
        assert "opencv" in deps
        assert "pytesseract" in deps
        assert "ffmpeg" in deps

    def test_list_commands(self):
        from src.mcp.surface_mcp_tools_handler import vision_list_commands
        result = vision_list_commands()
        data = json.loads(result)
        assert "image" in data
        assert "video" in data
        assert "memory" in data

    def test_list_commands_image(self):
        from src.mcp.surface_mcp_tools_handler import vision_list_commands
        result = vision_list_commands(domain="image")
        data = json.loads(result)
        assert len(data) == 4

    def test_help_all(self):
        from src.mcp.surface_mcp_tools_handler import vision_help
        result = vision_help()
        assert len(result) > 100

    def test_cancel_empty(self):
        from src.mcp.surface_mcp_tools_handler import vision_cancel
        result = json.loads(vision_cancel())
        assert "active_jobs" in result

    def test_cancel_unknown(self):
        from src.mcp.surface_mcp_tools_handler import vision_cancel
        result = json.loads(vision_cancel(job_id="invalid"))
        assert "error" in result


class TestMCPExecute:
    def test_execute_analyze_no_image(self):
        from src.mcp.surface_mcp_tools_handler import vision_execute
        result = json.loads(vision_execute(command="analyze"))
        assert "error" in result

    def test_execute_unknown_command(self):
        from src.mcp.surface_mcp_tools_handler import vision_execute
        result = json.loads(vision_execute(command="nonexistent"))
        assert "error" in result

    def test_execute_ocr_no_image(self):
        from src.mcp.surface_mcp_tools_handler import vision_execute
        result = json.loads(vision_execute(command="ocr"))
        assert "error" in result

    def test_execute_elements_no_image(self):
        from src.mcp.surface_mcp_tools_handler import vision_execute
        result = json.loads(vision_execute(command="elements"))
        assert "error" in result


class TestCLIEntry:
    def test_entry_module_imports(self):
        from src import cli_entry
        assert callable(cli_entry.cli)

    def test_mcp_entry_module_imports(self):
        from src import mcp_entry
        assert callable(mcp_entry.main)

    def test_tui_entry_module_imports(self):
        from src import tui_entry
        assert callable(tui_entry.main)


class TestTracking:
    def test_tracking_import(self):
        from src.tracking.capabilities_object_tracking_tracker import ObjectTrackingTracker
        from src.opencv.infrastructure_opencv_image_adapter import OpenCVImageAdapter
        tracker = ObjectTrackingTracker(OpenCVImageAdapter())
        assert tracker is not None
