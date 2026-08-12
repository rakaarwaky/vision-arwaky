#!/usr/bin/env python3
"""Export all Python skill directories into a single consolidated Markdown file.

The output includes all files within Python skill directories under `.agents/skills/`.
By default, running this script automatically collects and exports all Python skills
(skills ending with `-python` or `create-skill-all`).

Usage:
    # Automatic mode (exports all Python skills into python_skills_pack.md):
    python3 scripts/export/export_skill.py

    # CLI mode for a single skill:
    python3 scripts/export/export_skill.py --skill add-docs-python

    # Specify custom output path:
    python3 scripts/export/export_skill.py --output /tmp/custom_skills.md
"""

import argparse
import re
import sys
from pathlib import Path

# Sanitize version strings to a safe filename fragment (CWE-22 mitigation).
SAFE_VERSION_CHARS = re.compile(r"[^0-9A-Za-z.\-]")


def resolve_project_root() -> tuple[Path, Path]:
    """Return (project_root, skills_dir). Exit on missing .agents/skills/."""
    project_root = Path(__file__).resolve().parent.parent.parent
    skills_dir = project_root / ".agents" / "skills"

    if not skills_dir.exists():
        print(f"Error: '.agents/skills' directory not found at {skills_dir}", file=sys.stderr)
        sys.exit(1)
    return project_root, skills_dir


def list_skill_dirs(skills_dir: Path, lang: str = "python") -> list[str]:
    """Sorted list of skill directory names filtered by language.

    If lang is 'python', returns directories ending with '-python' or 'create-skill-all'.
    If lang is 'all', returns all skill directories.
    Otherwise, returns directories ending with f'-{lang}'.
    """
    skill_dirs = []
    lang_lower = lang.lower() if lang else "all"

    for entry in sorted(skills_dir.iterdir()):
        if not entry.is_dir() or entry.name.startswith("-") or entry.name == "exports":
            continue

        if lang_lower == "all":
            skill_dirs.append(entry.name)
        elif lang_lower == "python":
            if entry.name.endswith("-python") or entry.name == "create-skill-all":
                skill_dirs.append(entry.name)
        else:
            if entry.name.endswith(f"-{lang_lower}"):
                skill_dirs.append(entry.name)

    return sorted(skill_dirs)


def collect_skill_files(skill_path: Path) -> set[Path]:
    """Collect all files within the skill directory."""
    files: set[Path] = set()
    if not skill_path.exists():
        return files

    for f in skill_path.rglob("*"):
        if f.is_file():
            files.add(f)

    return files


def _language_for(path: Path) -> str:
    """Pick a fenced-code-block language identifier based on file extension."""
    if path.name == "pyproject.toml":
        return "toml"
    if path.suffix == ".py":
        return "python"
    if path.suffix in (".js", ".ts"):
        return "javascript"
    if path.suffix == ".md":
        return "markdown"
    if path.suffix in (".yaml", ".yml"):
        return "yaml"
    if path.suffix == ".json":
        return "json"
    if path.suffix == ".rs":
        return "rust"
    return ""


def write_markdown(
    output_path: Path,
    sorted_files: list[Path],
    project_root: Path,
    title: str,
) -> None:
    with open(output_path, "w", encoding="utf-8") as out:
        out.write(f"# Skill Pack: {title}\n\n")
        out.write(
            f"This document contains files for skill pack `{title}` "
            "from `.agents/skills/`.\n\n"
        )

        out.write("## File List\n\n")
        for f in sorted_files:
            rel = f.relative_to(project_root)
            out.write(f"- [{rel}]({f.as_uri()})\n")
        out.write("\n---\n\n")

        for f in sorted_files:
            rel = f.relative_to(project_root)
            out.write(f"## File: {rel}\n\n")
            lang = _language_for(f)
            if lang:
                out.write(f"```{lang}\n")
            else:
                out.write("```\n")
            try:
                content = f.read_text(encoding="utf-8", errors="replace")
                escaped = content.replace("```", "``` `")
                out.write(escaped)
                if not content.endswith("\n"):
                    out.write("\n")
            except OSError as e:
                out.write(f"/* Error reading file: {e} */\n")
            out.write("```\n\n---\n\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export Python skill directories into a consolidated Markdown file automatically."
    )
    parser.add_argument(
        "--skill", "-s",
        help="Export a specific skill name. Omit to automatically export all Python skills.",
    )
    parser.add_argument(
        "--lang", "-l",
        default="python",
        help="Filter skills by language ('python', 'rust', 'typescript', 'all'). Default: python.",
    )
    parser.add_argument(
        "--output", "-o",
        help="Output file path (default: .agents/skills/exports/python_skills_pack.md).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    project_root, skills_dir = resolve_project_root()

    if args.skill:
        # Export single specific skill
        all_skill_dirs = list_skill_dirs(skills_dir, lang="all")
        if args.skill not in all_skill_dirs:
            print(f"Error: Skill '{args.skill}' not found. Available: {', '.join(all_skill_dirs)}", file=sys.stderr)
            sys.exit(1)

        selected_skill = args.skill
        print(f"Processing skill: {selected_skill}...")

        skill_path = skills_dir / selected_skill
        files_to_export = collect_skill_files(skill_path)

        output_path = Path(args.output) if args.output else skills_dir / "exports" / f"{selected_skill}.md"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        print(f"Collecting {len(files_to_export)} file(s)...")
        sorted_files = sorted(files_to_export)

        print(f"Writing export to {output_path}...")
        write_markdown(output_path, sorted_files, project_root, selected_skill)
        print(f"\nSuccess! Consolidated markdown file created: {output_path}")
        return

    # Automatic mode: export all matching skills for target language (default: python)
    matching_skills = list_skill_dirs(skills_dir, lang=args.lang)
    if not matching_skills:
        print(f"Error: No skills found for language '{args.lang}'.", file=sys.stderr)
        sys.exit(1)

    print(f"Automatically exporting {len(matching_skills)} skill(s) for language '{args.lang}'...")
    all_files: set[Path] = set()
    for s in matching_skills:
        skill_path = skills_dir / s
        all_files.update(collect_skill_files(skill_path))

    pack_name = f"{args.lang}_skills_pack"
    output_path = Path(args.output) if args.output else skills_dir / "exports" / f"{pack_name}.md"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    sorted_files = sorted(all_files)
    print(f"Writing export to {output_path}...")
    write_markdown(output_path, sorted_files, project_root, pack_name)
    print(f"\nSuccess! Consolidated markdown file created: {output_path}")


if __name__ == "__main__":
    main()
