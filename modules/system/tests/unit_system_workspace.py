"""Unit and integration tests for workspace provisioner."""

from pathlib import Path

from modules.shared.src.taxonomy_vision_constant import EMBEDDED_SKILL_MD
from modules.shared.src.taxonomy_vision_vo import FilePath
from modules.system.src.capabilities_system_workspace import (
    CapabilitiesSystemWorkspace,
)


class TestWorkspaceProvisioner:
    """Test workspace initialization logic."""

    def test_init_workspace_with_git_repo_uses_git_info_exclude(self, tmp_path: Path):
        git_dir = tmp_path / ".git"
        git_dir.mkdir()

        provisioner = CapabilitiesSystemWorkspace()
        result = provisioner.init_workspace(FilePath(value=str(tmp_path)))

        assert "skill_md" in result
        skill_file = tmp_path / ".agents" / "skills" / "vision-arwaky" / "SKILL.md"
        assert skill_file.exists()
        assert skill_file.read_text(encoding="utf-8") == EMBEDDED_SKILL_MD

        dot_vision = tmp_path / ".vision-arwaky"
        assert dot_vision.exists()
        assert (dot_vision / "log").exists()
        assert (dot_vision / "data").exists()
        assert (dot_vision / "cache").exists()

        exclude_file = git_dir / "info" / "exclude"
        assert exclude_file.exists()
        content = exclude_file.read_text(encoding="utf-8")
        assert ".vision-arwaky" in content
        assert ".venv" in content
        assert "exclude" in result["git_exclude"]

    def test_init_workspace_without_git_uses_gitignore(self, tmp_path: Path):
        provisioner = CapabilitiesSystemWorkspace()
        result = provisioner.init_workspace(FilePath(value=str(tmp_path)))

        git_ignore = tmp_path / ".gitignore"
        assert git_ignore.exists()
        content = git_ignore.read_text(encoding="utf-8")
        assert ".vision-arwaky" in content
        assert ".venv" in content
        assert "gitignore" in result["git_exclude"]

    def test_init_workspace_idempotent_git_exclude(self, tmp_path: Path):
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        info_dir = git_dir / "info"
        info_dir.mkdir()
        exclude_file = info_dir / "exclude"
        exclude_file.write_text(".vision-arwaky\n.venv\n", encoding="utf-8")

        provisioner = CapabilitiesSystemWorkspace()
        result = provisioner.init_workspace(FilePath(value=str(tmp_path)))

        assert result["git_exclude"] == "exclude already contains required entries"
