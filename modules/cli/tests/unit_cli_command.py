"""Unit and integration tests for CLI init command."""

import json
from pathlib import Path

from modules.cli.src.surface_cli_command import cmd_init, set_cli_dispatcher
from modules.cli.src.surface_cli_controller import create_parser
from modules.mcp.src.surface_mcp_command import (
    set_mcp_dispatcher,
    vision_init,
)
from modules.system.src.root_system_container import SystemContainer


class TestWorkspaceSurfaces:
    """Test CLI and MCP surface integration for init."""

    def test_cli_init_command(self, tmp_path: Path, capsys):
        """Verify CLI init command creates workspace files."""
        set_cli_dispatcher(SystemContainer().orchestrator)
        parser = create_parser()
        args = parser.parse_args(["init", str(tmp_path)])
        assert args.command == "init"
        assert args.target_dir == str(tmp_path)

        ret = cmd_init(args)
        assert ret == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert "xdg_config" in data
        assert (tmp_path / ".vision-arwaky").exists()

    def test_mcp_vision_init_tool(self, tmp_path: Path):
        """Verify MCP vision_init tool creates workspace files."""
        set_mcp_dispatcher(SystemContainer().orchestrator)
        result_raw = vision_init(target_dir=str(tmp_path))
        data = json.loads(result_raw)
        assert "xdg_config" in data
        assert (tmp_path / ".vision-arwaky").exists()
