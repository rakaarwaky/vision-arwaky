"""TUI entry point for vision-arwaky configuration."""

from modules.cli.src.surface_tui_component import set_tui_dispatcher, tui_main
from modules.root_composition_container import build


def main():
    graph = build()
    set_tui_dispatcher(graph["dispatcher"])
    tui_main()


if __name__ == "__main__":
    main()
