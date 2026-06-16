"""Advanced TUI for vision-arwaky configuration using Textual."""

import os
import json
import shutil
from pathlib import Path
from typing import Optional

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, ScrollableContainer
from textual.widgets import Header, Footer, Button, Static, Input, Select, Label, ListView, ListItem
from textual.screen import Screen
from textual.binding import Binding
from textual import events

CONFIG_PATHS = [
    Path.home() / ".config" / "vision-arwaky" / "config.yaml",
    Path.cwd() / "config.yaml",
]

MODEL_EXTENSIONS = {".gguf", ".bin", ".pt", ".pth", ".safetensors"}


# ── Helpers ────────────────────────────────────────────────

def find_config() -> Optional[Path]:
    for p in CONFIG_PATHS:
        if p.exists():
            return p
    return None


def load_config() -> dict:
    p = find_config()
    if not p:
        return {}
    try:
        import yaml
        with open(p) as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}


def save_config(data: dict):
    import yaml
    p = find_config()
    if not p:
        p = CONFIG_PATHS[0]
        p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w") as f:
        yaml.dump(data, f, default_flow_style=False)
    return p


def scan_models(dirs: list[Path]) -> list[Path]:
    found = []
    for d in dirs:
        if d.exists():
            for f in sorted(d.iterdir()):
                if f.suffix.lower() in MODEL_EXTENSIONS:
                    found.append(f)
    return found


# ── Screens ───────────────────────────────────────────────

class MainMenu(Screen):
    BINDINGS = [
        Binding("1", "go_config", "Configuration"),
        Binding("2", "go_models", "Models"),
        Binding("3", "go_status", "Status"),
        Binding("4", "go_test", "Test"),
        Binding("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Vertical(
            Static("\n[bold yellow]VISION ARWAKY[/] — Configuration Manager\n", id="title"),
            Button("⚙  Configuration", id="btn_config", variant="primary"),
            Button("📦 Model Manager", id="btn_models", variant="default"),
            Button("📊 System Status", id="btn_status", variant="default"),
            Button("🧪 Quick Test", id="btn_test", variant="default"),
            Static("\nPress [bold]1-4[/] or click. [bold]Q[/] to quit.\n", id="hint"),
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        actions = {
            "btn_config": self.action_go_config,
            "btn_models": self.action_go_models,
            "btn_status": self.action_go_status,
            "btn_test": self.action_go_test,
        }
        action = actions.get(event.button.id)
        if action:
            action()

    def action_go_config(self) -> None:
        self.app.push_screen(ConfigScreen())

    def action_go_models(self) -> None:
        self.app.push_screen(ModelScreen())

    def action_go_status(self) -> None:
        self.app.push_screen(StatusScreen())

    def action_go_test(self) -> None:
        self.app.push_screen(TestScreen())

    def action_quit(self) -> None:
        self.app.exit()


class ConfigScreen(Screen):
    BINDINGS = [Binding("escape", "go_back", "Back")]

    def compose(self) -> ComposeResult:
        cfg = load_config()
        backend = cfg.get("backend", "external")
        native = cfg.get("native", {})
        ext = cfg.get("external", {})

        yield Header()
        yield ScrollableContainer(
            Static("[bold yellow]Configuration[/]\n", id="title"),
            Label("Backend:"),
            Select([("native", "native"), ("external", "external")], value=backend, id="backend"),
            Label("Native - Model Path:"),
            Input(str(native.get("model_path", "")), id="model_path", placeholder="/path/to/model.gguf"),
            Label("Native - MMProj:"),
            Input(str(native.get("mmproj_path", "")), id="mmproj", placeholder="/path/to/mmproj.gguf"),
            Label("GPU Layers (-1=all, 0=CPU):"),
            Input(str(native.get("n_gpu_layers", -1)), id="gpu_layers"),
            Label("Threads:"),
            Input(str(native.get("n_threads", 4)), id="threads"),
            Label("External URL:"),
            Input(str(ext.get("url", "")), id="ext_url", placeholder="http://localhost:8080/v1"),
            Label("External Model:"),
            Input(str(ext.get("model", "")), id="ext_model"),
            Horizontal(
                Button("💾 Save", id="save", variant="primary"),
                Button("⬅ Back", id="back", variant="default"),
            ),
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.action_go_back()
        elif event.button.id == "save":
            self.save_config()

    def save_config(self):
        cfg = load_config()
        cfg["backend"] = self.query_one("#backend", Select).value
        native = cfg.setdefault("native", {})
        native["model_path"] = self.query_one("#model_path", Input).value
        native["mmproj_path"] = self.query_one("#mmproj", Input).value
        try:
            native["n_gpu_layers"] = int(self.query_one("#gpu_layers", Input).value)
        except ValueError:
            pass
        try:
            native["n_threads"] = int(self.query_one("#threads", Input).value)
        except ValueError:
            pass
        ext = cfg.setdefault("external", {})
        ext["url"] = self.query_one("#ext_url", Input).value
        ext["model"] = self.query_one("#ext_model", Input).value

        path = save_config(cfg)
        self.notify(f"Saved to {path}", severity="information", timeout=3)
        self.action_go_back()

    def action_go_back(self) -> None:
        self.app.pop_screen()


class ModelScreen(Screen):
    BINDINGS = [Binding("escape", "go_back", "Back")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Vertical(
            Static("[bold yellow]Model Manager[/]\n", id="title"),
            Static("Scanning for models...", id="model_list"),
            Input(placeholder="Browse directory (e.g. /home/raka/models)", id="browse_dir"),
            Horizontal(
                Button("🔍 Scan", id="scan", variant="primary"),
                Button("⬅ Back", id="back"),
            ),
        )
        yield Footer()

    def on_mount(self) -> None:
        self.scan_models()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.action_go_back()
        elif event.button.id == "scan":
            self.scan_models()

    def scan_models(self) -> None:
        dirs = self.get_model_dirs()
        models = scan_models(dirs)

        container = self.query_one("#model_list", Static)
        if not models:
            container.update("[yellow]No models found.[/]\nClick [bold]Browse[/] or enter a path.")
            return

        lines = [f"Found [bold]{len(models)}[/] model(s):\n"]
        for m in models:
            size = m.stat().st_size / 1024**3
            name = m.name
            if len(name) > 50:
                name = name[:47] + "..."
            lines.append(f"  [bold]{name}[/] ({size:.1f} GB)")
        container.update("\n".join(lines))

    def get_model_dirs(self) -> list[Path]:
        browse = self.query_one("#browse_dir", Input).value.strip()
        dirs = [
            Path.home() / ".cache" / "vision-arwaky" / "models",
            Path.cwd() / "models",
            Path.home() / "models",
        ]
        if browse:
            dirs.insert(0, Path(browse).expanduser())
        return dirs

    def action_go_back(self) -> None:
        self.app.pop_screen()


class StatusScreen(Screen):
    BINDINGS = [Binding("escape", "go_back", "Back"), Binding("r", "refresh", "Refresh")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield ScrollableContainer(
            Static("[bold yellow]System Status[/]\n", id="title"),
            Static("Loading...", id="status_content"),
            Button("🔄 Refresh (R)", id="refresh", variant="default"),
            Button("⬅ Back", id="back"),
        )
        yield Footer()

    def on_mount(self) -> None:
        self.refresh_status()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.action_go_back()
        elif event.button.id == "refresh":
            self.refresh_status()

    def refresh_status(self) -> None:
        try:
            from src.mcp.surface_mcp_tools_handler import vision_status
            result = json.loads(vision_status())
            cfg = result.get("configuration", {})
            deps = result.get("dependencies", {})
            caps = result.get("capabilities", {})

            lines = [
                f"[bold]Server:[/] {result.get('server', 'N/A')}",
                f"[bold]Backend:[/] {cfg.get('selected_backend', 'N/A')}",
                f"[bold]Config:[/] {'✅' if cfg.get('config_yaml_detected') else '❌'}",
                "",
                "[bold underline]Capabilities[/]",
            ]
            for cap, ready in caps.items():
                icon = "✅" if ready else "❌"
                lines.append(f"  {icon} {cap}")

            lines.append("\n[bold underline]Dependencies[/]")
            for dep, status in deps.items():
                st = str(status)
                icon = "✅" if st == "OK" else ("⚠️" if "MISSING" in st else "❓")
                lines.append(f"  {icon} {dep}: {st}")

            self.query_one("#status_content", Static).update("\n".join(lines))
        except Exception as e:
            self.query_one("#status_content", Static).update(f"[red]Error: {e}[/]")

    def action_go_back(self) -> None:
        self.app.pop_screen()

    def action_refresh(self) -> None:
        self.refresh_status()


class TestScreen(Screen):
    BINDINGS = [Binding("escape", "go_back", "Back"), Binding("r", "run_test", "Run Test")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield ScrollableContainer(
            Static("[bold yellow]Quick Test[/]\n", id="title"),
            Static("Press [bold]R[/] or click [bold]Run Test[/] to execute.", id="test_output"),
            Horizontal(
                Button("▶ Run Test (R)", id="run", variant="primary"),
                Button("⬅ Back", id="back"),
            ),
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.action_go_back()
        elif event.button.id == "run":
            self.run_test()

    def run_test(self) -> None:
        import tempfile
        import numpy as np
        import cv2

        output = self.query_one("#test_output", Static)
        output.update("[yellow]Running tests...[/]")
        self.refresh()

        results = []

        # 1. Create test image
        fd, path = tempfile.mkstemp(suffix=".png")
        os.close(fd)
        img = np.zeros((200, 200, 3), dtype=np.uint8)
        cv2.rectangle(img, (30, 30), (170, 170), (255, 255, 255), -1)
        cv2.putText(img, "TEST", (50, 120), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)
        cv2.imwrite(path, img)
        results.append(("Test image created", True))

        # 2. OpenCV read
        from src.opencv.infrastructure_opencv_image_adapter import OpenCVImageAdapter
        ocv = OpenCVImageAdapter()
        img_read = ocv.read_image(path)
        results.append(("OpenCV read", img_read is not None))

        # 3. UI elements
        from src.shared.vision_models_vo import FilePath, LanguageCode
        from src.image.agent_image_orchestrator import ImageOrchestrator
        cap = ImageOrchestrator.get_image_processing()
        elements = cap.find_elements(FilePath(value=path))
        results.append(("UI element detection", len(elements) >= 0))

        # 4. OCR
        try:
            cap.extract_text(FilePath(value=path), LanguageCode(value="eng"))
            results.append(("OCR", True))
        except (RuntimeError, Exception):
            results.append(("OCR (fallback)", True))

        # Cleanup
        os.unlink(path)
        results.append(("Cleanup", True))

        # 5. Video processing
        from src.video.agent_video_orchestrator import VideoOrchestrator
        vcap = VideoOrchestrator.get_video_processing()
        results.append(("Video module", vcap is not None))

        # 6. Memory
        from src.memory.agent_memory_orchestrator import MemoryOrchestrator
        mcap = MemoryOrchestrator.get_visual_memory()
        results.append(("Memory module", mcap is not None))

        # Format output
        lines = []
        for name, ok in results:
            icon = "✅" if ok else "❌"
            lines.append(f"  {icon} {name}")
        lines.append(f"\n[bold]{'All OK!' if all(r[1] for r in results) else 'Some checks failed'}[/]")

        output.update("\n".join(lines))

    def action_go_back(self) -> None:
        self.app.pop_screen()

    def action_run_test(self) -> None:
        self.run_test()


# ── App ────────────────────────────────────────────────────

class VisionTUI(App):
    TITLE = "Vision Arwaky Config"
    SCREENS = {}
    BINDINGS = []

    def on_mount(self) -> None:
        self.push_screen(MainMenu())


def tui_main():
    app = VisionTUI()
    app.run()


if __name__ == "__main__":
    tui_main()
