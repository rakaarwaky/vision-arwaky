"""Configuration utilities — stateless helpers for config file handling."""

from pathlib import Path

CONFIG_PATHS = [
    Path.home() / ".config" / "vision-arwaky" / "config.yaml",
    Path.cwd() / "config.yaml",
]

MODEL_EXTENSIONS = {".gguf", ".bin", ".pt", ".pth", ".safetensors"}


def find_config() -> Path | None:
    """Locate the active config file, if any."""
    for p in CONFIG_PATHS:
        if p.exists():
            return p
    return None


def load_config() -> dict:
    """Load config YAML into a dict (empty on missing/invalid/non-mapping file)."""
    p = find_config()
    if not p:
        return {}
    try:
        import yaml

        with open(p) as f:
            data = yaml.safe_load(f)
        if not isinstance(data, dict):
            return {}
        return data
    except (OSError, yaml.YAMLError):
        return {}


def save_config(data: dict) -> Path:
    """Persist config dict to the active (or default) config path."""
    import yaml

    p = find_config()
    if not p:
        p = CONFIG_PATHS[0]
        p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w") as f:
        yaml.dump(data, f, default_flow_style=False)
    return p


def scan_models(dirs: list[Path]) -> list[Path]:
    """Scan directories for supported model files."""
    found = []
    for d in dirs:
        if d.exists():
            for f in sorted(d.iterdir()):
                if f.suffix.lower() in MODEL_EXTENSIONS:
                    found.append(f)
    return found
