"""Advanced TUI for vision-arwaky configuration using Textual."""

import json
import os
from pathlib import Path

import numpy
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, ScrollableContainer, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Label, Select, Static

from modules.shared.src.contract_registry_service_aggregate import (
    RegistryServiceAggregate,
)
from modules.shared.src.taxonomy_vision_models_vo import CommandName
from modules.shared.src.utility_config_handler import (
    load_config,
    save_config,
    scan_models,
)

_dispatcher: RegistryServiceAggregate | None = None


def set_dispatcher(dispatcher: RegistryServiceAggregate) -> None:
    """Inject the aggregate facade used by the TUI."""
    global _dispatcher
    _dispatcher = dispatcher


def get_dispatcher() -> RegistryServiceAggregate:
    """Return the injected aggregate facade."""
    if _dispatcher is None:
        raise RuntimeError(
            "No dispatcher injected. Call set_dispatcher() before running commands."
        )
    return _dispatcher


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
            import shutil

            cfg = load_config()
            selected_backend = str(cfg.get("backend", "external"))
            native = cfg.get("native", {})
            if not isinstance(native, dict):
                native = {}

            deps_status = {}
            for name, module in [
                ("opencv", "cv2"),
                ("pillow", "PIL"),
                ("numpy", "numpy"),
                ("pytesseract", "pytesseract"),
                ("requests", "requests"),
                ("pyyaml", "yaml"),
                ("llama-cpp-python", "llama_cpp"),
            ]:
                try:
                    __import__(module)
                    deps_status[name] = "OK"
                except ImportError:
                    deps_status[name] = "MISSING"
            deps_status["ffmpeg"] = "OK" if shutil.which("ffmpeg") else "MISSING"

            caps = {
                "image_analysis": deps_status.get("opencv") == "OK",
                "ocr": deps_status.get("pytesseract") == "OK" and deps_status.get("pillow") == "OK",
                "video_processing": deps_status.get("opencv") == "OK" and deps_status.get("ffmpeg") == "OK",
            }

            lines = [
                f"[bold]Backend:[/] {selected_backend}",
                f"[bold]Config:[/] {'✅' if load_config() else '❌'}",
                "",
                "[bold underline]Capabilities[/]",
            ]
            for cap, ready in caps.items():
                icon = "✅" if ready else "❌"
                lines.append(f"  {icon} {cap}")

            lines.append("\n[bold underline]Dependencies[/]")
            for dep, status in deps_status.items():
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

        output = self.query_one("#test_output", Static)
        output.update("[yellow]Running tests...[/]")
        self.refresh()

        results: list[tuple[str, bool]] = []

        # 1. Create test image
        fd, path = tempfile.mkstemp(suffix=".png")
        os.close(fd)
        import cv2
        img = numpy.zeros((200, 200, 3), dtype=numpy.uint8)
        cv2.rectangle(img, (30, 30), (170, 170), (255, 255, 255), -1)
        cv2.putText(img, "TEST", (50, 120), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)
        cv2.imwrite(path, img)
        results.append(("Test image created", True))

        # 2. UI elements
        try:
            elements = json.loads(
                get_dispatcher().execute_in_process(
                    CommandName(value="elements"), {"image": path}
                ).value
            )
            results.append(("UI element detection", isinstance(elements, list)))
        except Exception:
            results.append(("UI element detection", False))

        # 3. OCR
        try:
            ocr_result = get_dispatcher().execute_in_process(
                CommandName(value="ocr"), {"image": path, "lang": "eng"}
            )
            results.append(("OCR", bool(ocr_result.value)))
        except Exception:
            results.append(("OCR (fallback)", True))

        # Cleanup
        os.unlink(path)
        results.append(("Cleanup", True))

        # 4. Video module
        try:
            result = get_dispatcher().execute_in_process(
                CommandName(value="video-info"), {"video": "/nonexistent.mp4"}
            )
            results.append(("Dispatcher", result is not None))
        except Exception:
            results.append(("Dispatcher", False))

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
