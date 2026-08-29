"""Unit tests for MCP action functions (vision_init, vision_execute)."""

import json
from pathlib import Path

from modules.mcp.src.surface_mcp_action import (
    set_mcp_dispatcher,
    vision_execute,
    vision_init,
    vision_list_commands,
)
from modules.system.src.root_system_container import SystemContainer


class TestMCPActions:
    def test_vision_init(self, tmp_path: Path):
        set_mcp_dispatcher(SystemContainer().orchestrator)
        result_raw = vision_init(target_dir=str(tmp_path))
        data = json.loads(result_raw)
        assert "skill_md" in data
        assert (tmp_path / ".agents" / "skills" / "vision-arwaky" / "SKILL.md").exists()

    def test_vision_execute_init(self, tmp_path: Path):
        set_mcp_dispatcher(SystemContainer().orchestrator)
        result_raw = vision_execute(command="init", target_dir=str(tmp_path))
        data = json.loads(result_raw)
        assert "skill_md" in data

    def test_list_commands_includes_workspace(self):
        result = json.loads(vision_list_commands())
        assert "workspace" in result
        assert result["workspace"][0]["command"] == "init"
