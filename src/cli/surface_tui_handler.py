"""TUI surface — terminal UI for configuration and system management."""

import os
import sys
import json
from pathlib import Path
from typing import Optional

CONFIG_PATHS = [
    Path.home() / ".config" / "vision-arwaky" / "config.yaml",
    Path.cwd() / "config.yaml",
]


def _find_config() -> Optional[Path]:
    for p in CONFIG_PATHS:
        if p.exists():
            return p
    return None


def _cmd_help():
    print("""
╔══════════════════════════════════════════════╗
║        Vision Arwaky — TUI Config            ║
╠══════════════════════════════════════════════╣
║ 1) Show config                               ║
║ 2) Edit backend (native/external)            ║
║ 3) Set model path                            ║
║ 4) Set GPU layers                            ║
║ 5) Check dependencies                        ║
║ 6) Run quick test                            ║
║ 7) Show system status                        ║
║ h) Help                                      ║
║ q) Quit                                      ║
╚══════════════════════════════════════════════╝
""")


def _show_config():
    config_path = _find_config()
    if not config_path:
        print("✗ No config.yaml found")
        return
    try:
        import yaml
        with open(config_path) as f:
            data = yaml.safe_load(f) or {}
        print(f"\nConfig: {config_path}")
        print(json.dumps(data, indent=2))
    except Exception as e:
        print(f"✗ Failed to read config: {e}")


def _edit_backend():
    config_path = _find_config()
    if not config_path:
        print("✗ No config.yaml found. Run install script first.")
        return
    try:
        import yaml
        with open(config_path) as f:
            data = yaml.safe_load(f) or {}
    except Exception:
        data = {}

    current = data.get("backend", "external")
    print(f"\nCurrent backend: {current}")
    print("1) native (llama-cpp-python, in-process)")
    print("2) external (API server, e.g. llama-server)")
    choice = input("Select backend [1/2]: ").strip()

    if choice == "1":
        data["backend"] = "native"
    elif choice == "2":
        data["backend"] = "external"
    else:
        print("✗ Invalid choice")
        return

    with open(config_path, "w") as f:
        yaml.dump(data, f, default_flow_style=False)
    print(f"✓ Backend set to: {data['backend']}")


def _check_deps():
    deps = {
        "cv2": "opencv-python",
        "PIL": "pillow",
        "requests": "requests",
        "yaml": "pyyaml",
        "pytesseract": "pytesseract",
        "llama_cpp": "llama-cpp-python",
    }
    print("\nDependencies:")
    for mod, pkg in deps.items():
        try:
            __import__(mod)
            print(f"  ✓ {pkg}")
        except ImportError:
            print(f"  ✗ {pkg}")

    import shutil
    print(f"  {'✓' if shutil.which('ffmpeg') else '✗'} ffmpeg (binary)")


def _system_status():
    """Show system status via MCP status tool."""
    try:
        from src.mcp import vision_status
        result = json.loads(vision_status())
        print(f"\nServer: {result.get('server', 'N/A')}")
        print(f"Backend: {result.get('configuration', {}).get('selected_backend', 'N/A')}")
        print(f"Config: {'✓ Found' if result.get('configuration', {}).get('config_yaml_detected') else '✗ Not found'}")
        print("\nCapabilities:")
        for cap, ready in result.get('capabilities', {}).items():
            print(f"  {'✓' if ready else '✗'} {cap}")
        print("\nDependencies:")
        for dep, status in result.get('dependencies', {}).items():
            icon = "✓" if status == "OK" else "✗"
            print(f"  {icon} {dep}: {status}")
    except Exception as e:
        print(f"✗ Status check failed: {e}")


def _quick_test():
    """Run a quick image processing test."""
    import tempfile
    import numpy as np
    import cv2

    print("\nRunning quick test...")
    fd, path = tempfile.mkstemp(suffix=".png")
    os.close(fd)
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    cv2.rectangle(img, (20, 20), (80, 80), (255, 255, 255), -1)
    cv2.imwrite(path, img)

    try:
        from src.image.agent_image_orchestrator import ImageOrchestrator
        cap = ImageOrchestrator.get_image_processing()
        from src.shared.vision_models_vo import FilePath
        elements = cap.find_elements(FilePath(value=path))
        print(f"  ✓ Image loaded, found {len(elements)} UI elements")
        os.unlink(path)
        print("  ✓ Cleanup OK")
    except Exception as e:
        print(f"  ✗ Test failed: {e}")
        try:
            os.unlink(path)
        except OSError:
            pass


def tui_main():
    """Main TUI loop."""
    print("\nVision Arwaky — Configuration TUI")
    print("=" * 40)
    _cmd_help()

    while True:
        try:
            cmd = input("\n> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if cmd in ("q", "quit", "exit"):
            print("Goodbye!")
            break
        elif cmd in ("h", "help", "?"):
            _cmd_help()
        elif cmd == "1":
            _show_config()
        elif cmd == "2":
            _edit_backend()
        elif cmd == "3":
            print("Coming soon: set model path via menu")
        elif cmd == "4":
            print("Coming soon: set GPU layers via menu")
        elif cmd == "5":
            _check_deps()
        elif cmd == "6":
            _quick_test()
        elif cmd == "7":
            _system_status()
        elif cmd == "":
            continue
        else:
            print(f"Unknown command: {cmd}. Type 'h' for help.")


if __name__ == "__main__":
    tui_main()
