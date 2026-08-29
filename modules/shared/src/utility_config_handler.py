"""Configuration utilities — stateless pure functions (XDG-aware)."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

from modules.shared.src.taxonomy_xdg_paths_vo import XDGPaths

DEFAULT_LLM_URL = "http://127.0.0.1:1234/v1"
MODEL_EXTENSIONS = {".gguf", ".bin", ".pt", ".pth", ".safetensors"}


def get_user_config_path() -> Path:
    """Return user XDG configuration path."""
    return XDGPaths.config_dir() / "config.yaml"


def get_local_config_path() -> Path:
    """Return local directory configuration path."""
    return Path.cwd() / "config.yaml"


def find_active_config(
    user_path: Path | None = None,
    local_path: Path | None = None,
) -> Path | None:
    """Find active configuration path with precedence: user XDG > local cwd."""
    u_path = user_path or get_user_config_path()
    l_path = local_path if local_path is not None else get_local_config_path()
    if u_path.exists():
        return u_path
    if l_path.exists():
        return l_path
    return None


def find_config() -> Path | None:
    """Alias for finding active configuration path."""
    return find_active_config()


def read_yaml_config(path: Path) -> dict[str, Any]:
    """Read a YAML file into a dictionary safely."""
    if not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as f:
            content = yaml.safe_load(f)
            return content if isinstance(content, dict) else {}
    except (OSError, yaml.YAMLError):
        return {}


def load_config() -> dict[str, Any]:
    """Load active configuration file dictionary."""
    p = find_active_config()
    if not p:
        return {}
    return read_yaml_config(p)


def load_merged_config(
    user_path: Path | None = None,
    local_path: Path | None = None,
) -> dict[str, Any]:
    """Merge local fallback, user XDG config, and environment overrides."""
    u_path = user_path or get_user_config_path()
    l_path = local_path if local_path is not None else get_local_config_path()

    local_cfg = read_yaml_config(l_path)
    user_cfg = read_yaml_config(u_path)
    merged: dict[str, Any] = {**local_cfg, **user_cfg}

    if "external" in local_cfg and "external" in user_cfg:
        merged["external"] = {**local_cfg["external"], **user_cfg["external"]}

    if os.getenv("LLAMA_API_URL"):
        merged.setdefault("external", {})["url"] = os.getenv("LLAMA_API_URL")
    if os.getenv("LLAMA_API_KEY"):
        merged.setdefault("external", {})["api_key"] = os.getenv("LLAMA_API_KEY")
    if os.getenv("LLAMA_MODEL"):
        merged.setdefault("external", {})["model"] = os.getenv("LLAMA_MODEL")

    return merged


def resolve_external_settings(
    config: dict[str, Any] | None = None,
) -> tuple[str, str, str]:
    """Resolve endpoint URL, API key, and model name."""
    cfg = config if config is not None else load_merged_config()
    external = cfg.get("external")
    ext = external if isinstance(external, dict) else {}

    url = (
        os.getenv("LLAMA_API_URL") or str(ext.get("url", "")) or DEFAULT_LLM_URL
    ).rstrip("/")
    api_key = os.getenv("LLAMA_API_KEY") or str(ext.get("api_key", ""))
    model = os.getenv("LLAMA_MODEL") or str(ext.get("model", ""))

    return url, api_key, model


def save_user_config(data: dict[str, Any], path: Path | None = None) -> Path:
    """Save configuration dictionary to user XDG path."""
    target_path = path or get_user_config_path()
    target_path.parent.mkdir(parents=True, exist_ok=True)
    with target_path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, default_flow_style=False)
    return target_path


def save_config(data: dict[str, Any]) -> Path:
    """Alias for saving user config."""
    p = find_active_config()
    target = p if p else get_user_config_path()
    return save_user_config(data, target)


def scan_models(dirs: list[Path]) -> list[Path]:
    """Scan directories for model files."""
    found: list[Path] = []
    for d in dirs:
        if d.exists():
            for f in sorted(d.iterdir()):
                if f.suffix.lower() in MODEL_EXTENSIONS:
                    found.append(f)
    return found
