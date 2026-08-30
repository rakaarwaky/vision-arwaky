# Plan: cli (v2.0.7) — Architect

## Summary

The `cli` module is a surface-only feature exposing the `vision-arwaky-cli` / `va` command surface and a Textual TUI. The CLI command path (`surface_cli_controller` → `surface_cli_command` → `RegistryServiceAggregate`) is architecturally sound: the parser is stateless, handlers delegate through the injected aggregate, and smart-surface import rules are respected.

## Findings

### Surface Compliance

| Component | Role | Status | Note |
| --- | --- | --- | --- |
| `surface_cli_controller.py` | Smart Surface (controller) | ✅ | Argparse parser creation, `prog="vision-arwaky-cli"` |
| `surface_cli_command.py` | Smart Surface (command) | ✅ | Delegates commands to aggregate |
| `surface_tui_controller.py` | Smart Surface (controller) | ✅ | Renamed from component; Textual app and screens |

### Action Items

- [x] **P0** Rename `surface_tui_component.py` → `surface_tui_controller.py` to correctly identify smart surface controller role.
- [x] **P1** Remove Utility→Utility import in `utility_frame_extractor.py` and call `cv2.VideoCapture` directly.
- [x] **P2** Align `prog="vision-arwaky-cli"` in `surface_cli_controller.py`.
