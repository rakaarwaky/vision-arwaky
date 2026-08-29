"""Capabilities: system workspace provisioner (AES403).

Implements WorkspaceProtocol — workspace initialization with XDG directories,
SKILL.md provisioning, .vision-arwaky symlinks, and .git/info/exclude management.
All file system I/O for workspace setup lives here.
"""

from __future__ import annotations

import os
from pathlib import Path

from modules.shared.src.contract_workspace_protocol import WorkspaceProtocol
from modules.shared.src.taxonomy_vision_constant import EMBEDDED_SKILL_MD
from modules.shared.src.taxonomy_vision_vo import FilePath
from modules.shared.src.taxonomy_xdg_paths_vo import XDGPaths
from modules.shared.src.utility_xdg_paths import ensure_xdg_dirs


# ─── Block 1: Class Definition & Constructor ──────────────
class CapabilitiesSystemWorkspace(WorkspaceProtocol):
    """Workspace directory provisioning with symlinks and git exclude management."""

    def __init__(self) -> None:
        """Initialize CapabilitiesSystemWorkspace."""

    # ─── Block 2: Public Contract (WorkspaceProtocol ONLY) ───
    def init_workspace(self, target_dir: FilePath) -> dict[str, str]:
        """Initialize workspace in sequential steps:

        Step 1: Ensure XDG directories exist
        Step 2: Provision .agents/skills/vision-arwaky/SKILL.md from embedded constant
        Step 3: Provision .vision-arwaky directory with symlinks to XDG paths
        Step 4: Update .git/info/exclude (or fallback to .gitignore) with .vision-arwaky and .venv
        """
        target_path = Path(target_dir.value).expanduser().resolve()
        created_items: dict[str, str] = {}

        # Step 1: Ensure XDG directories exist
        ensure_xdg_dirs()
        created_items["xdg_config"] = str(XDGPaths.config_dir())
        created_items["xdg_data"] = str(XDGPaths.data_dir())
        created_items["xdg_cache"] = str(XDGPaths.cache_dir())
        created_items["xdg_state"] = str(XDGPaths.state_dir())

        # Step 2: Create .agents/skills/vision-arwaky/SKILL.md from embedded constant
        skills_dir = target_path / ".agents" / "skills" / "vision-arwaky"
        skills_dir.mkdir(parents=True, exist_ok=True)
        skill_md_dest = skills_dir / "SKILL.md"
        skill_md_dest.write_text(EMBEDDED_SKILL_MD, encoding="utf-8")
        created_items["skill_md"] = str(skill_md_dest)

        # Step 3: Create .vision-arwaky directory with symlinks to XDG paths
        dot_vision = target_path / ".vision-arwaky"
        dot_vision.mkdir(parents=True, exist_ok=True)

        links: dict[str, Path] = {
            "log": XDGPaths.state_dir(),
            "data": XDGPaths.data_dir(),
            "cache": XDGPaths.cache_dir(),
        }

        for link_name, xdg_target in links.items():
            link_path = dot_vision / link_name
            self._ensure_symlink(link_path, xdg_target)
            created_items[f"link_{link_name}"] = f"{link_path} -> {xdg_target}"

        # Link .venv if XDG venv exists
        venv_xdg = XDGPaths.venv_dir()
        if venv_xdg.exists():
            dot_venv = target_path / ".venv"
            self._ensure_symlink(dot_venv, venv_xdg)
            created_items["link_venv"] = f"{dot_venv} -> {venv_xdg}"

        # Step 4: Ensure git ignores .vision-arwaky and .venv via .git/info/exclude
        exclude_result = self._ensure_git_exclude(target_path)
        created_items["git_exclude"] = exclude_result

        return created_items

    # ─── Block 3: Dunder Methods, Factories & Helpers ─────────
    def __repr__(self) -> str:
        """Return string representation of CapabilitiesSystemWorkspace."""
        return "CapabilitiesSystemWorkspace()"

    @staticmethod
    def _ensure_symlink(link_path: Path, target_path: Path) -> None:
        """Create or replace a symlink pointing to target_path.

        Only removes existing *symlinks* or *plain files*. Raises ``OSError``
        when ``link_path`` already exists as a real directory — callers must
        resolve that conflict explicitly rather than silently deleting data.
        If ``os.symlink`` fails, the error is re-raised so callers can report
        the actual outcome rather than misreporting success.
        """
        if link_path.is_symlink():
            link_path.unlink(missing_ok=True)
        elif link_path.is_dir():
            raise OSError(
                f"Cannot create symlink: '{link_path}' is a real directory. "
                "Remove or relocate it manually before initialising the workspace."
            )
        elif link_path.exists():
            link_path.unlink(missing_ok=True)

        os.symlink(target_path, link_path, target_is_directory=True)

    @staticmethod
    def _parse_git_dir_exclude(git_entry: Path, current: Path) -> Path | None:
        """Parse gitdir: line from a gitfile and return the exclude path."""
        try:
            line = git_entry.read_text(encoding="utf-8").strip()
            if line.startswith("gitdir:"):
                git_dir_raw = line.split("gitdir:", 1)[1].strip()
                git_dir = Path(git_dir_raw)
                if not git_dir.is_absolute():
                    git_dir = (current / git_dir).resolve()
                return git_dir / "info" / "exclude"
        except OSError:
            pass
        return None

    @classmethod
    def _find_git_exclude_file(cls, target_path: Path) -> Path | None:
        """Find .git/info/exclude in target_path or parent directory."""
        current: Path | None = target_path
        while current is not None:
            git_entry = current / ".git"
            if git_entry.is_dir():
                return git_entry / "info" / "exclude"
            if git_entry.is_file():
                exclude_file = cls._parse_git_dir_exclude(git_entry, current)
                if exclude_file is not None:
                    return exclude_file
            if current == current.parent:
                break
            current = current.parent
        return None

    @classmethod
    def _append_missing_entries(cls, target_file: Path, missing: list[str], entries: list[str]) -> str:
        """Append missing entries to an existing exclude file."""
        with target_file.open("a", encoding="utf-8") as f:
            for m in missing:
                f.write(f"\n{m}\n")
        return f"{target_file.name} updated with {', '.join(missing)}"

    @classmethod
    def _ensure_git_exclude(cls, target_path: Path) -> str:
        """Ignore workspace files in .git/info/exclude (preferred) or .gitignore."""
        entries = [".vision-arwaky", ".venv"]
        exclude_file = cls._find_git_exclude_file(target_path)
        target_file = (
            exclude_file if exclude_file is not None else (target_path / ".gitignore")
        )
        target_file.parent.mkdir(parents=True, exist_ok=True)

        if target_file.exists():
            content = target_file.read_text(encoding="utf-8")
            # Compare full patterns only; ignore comment lines to avoid false positives
            # (e.g. ".venv-backup" substring-matching ".venv").
            existing_patterns = {
                line.strip()
                for line in content.splitlines()
                if line.strip() and not line.strip().startswith("#")
            }
            missing = [e for e in entries if e not in existing_patterns]
            if missing:
                return cls._append_missing_entries(target_file, missing, entries)
            return f"{target_file.name} already contains required entries"

        target_file.write_text("\n".join(entries) + "\n", encoding="utf-8")
        return f"{target_file.name} created with {', '.join(entries)}"


__all__ = ["CapabilitiesSystemWorkspace"]
