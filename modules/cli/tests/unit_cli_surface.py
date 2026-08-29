"""Unit tests for CLI parser."""

from typing import Any

from modules.cli.src.surface_cli_controller import create_parser


class TestCLIParsing:
    def test_parser_registers_all_clean_commands(self):
        parser: Any = create_parser()
        expected_workspace = {"init"}
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
        subparsers_action = parser._subparsers
        choices = subparsers_action._group_actions[0].choices
        for cmd in expected_workspace | expected_image | expected_video:
            assert cmd in choices, f"Missing command in parser: {cmd}"

    def test_parser_excludes_bloat_commands(self):
        parser: Any = create_parser()
        subparsers_action = parser._subparsers
        choices = subparsers_action._group_actions[0].choices
        for cmd in ["elements", "convert", "create-gif", "timeline", "test"]:
            assert cmd not in choices, f"Bloat command still in parser: {cmd}"
