# Plan: mcp — Architect

## Summary

The `mcp` module (v2.0.7) is a surface-only adapter that exposes Vision Arwaky to AI agents via six FastMCP tools over stdio. It correctly delegates command execution through the `RegistryServiceAggregate` contract facade and reads system state through shared utilities. The core dependency direction is sound: Surface → Contract Aggregate + Taxonomy + Utility.

## Findings

### Surface Compliance

| Component | Role | Status | Note |
| --- | --- | --- | --- |
| `surface_mcp_command.py` | Smart Surface (command) | ✅ | FastMCP tools delegating to aggregate facade |
| `surface_mcp_controller.py` | Deprecated Stub | 🗑️ | Deleted dead code |

### Action Items

- [x] **P1** Rename `surface_mcp_action.py` → `surface_mcp_command.py` to align role name with smart-surface classification.
- [x] **P1** Delete `surface_mcp_controller.py` (deprecated, dead code).
- [x] **P1** Update `modules/mcp/src/__init__.py`: remove `_check_dependencies`, add `vision_init`, `set_mcp_dispatcher`, `get_dispatcher`.
