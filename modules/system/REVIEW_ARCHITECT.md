# Plan: system — Architect

## Summary

The `system` module (v2.0.7) is architecturally sound in its core structure: all five source files carry correct layer prefixes, the three capabilities implement their respective contract protocols, the agent orchestrator delegates exclusively through contract interfaces, and the root container wires concrete implementations via constructor injection. No critical layering breaches or circular dependencies were detected.

## Findings

### Capabilities & Agent Compliance (protocol / aggregate check)

| Component | Contract | Status | Note |
| --- | --- | --- | --- |
| `CapabilitiesSystemConfiguration` | `SystemConfigurationProtocol` | ✅ | Config reading and mutation implemented |
| `CapabilitiesSystemJob` | `SystemJobProtocol` | ✅ | Status reporting implemented; synchronous execution simplified |
| `CapabilitiesSystemWorkspace` | `WorkspaceProtocol` | ✅ | Workspace directory and symlink management implemented |
| `SystemOrchestrator` | `RegistryServiceAggregate` | ✅ | Aggregate implemented; dispatch map pattern applied |

### Action Items

- [x] **P1** Extract `XDGPaths` directory creation logic from taxonomy into `utility_xdg_paths.py` (LB-1).
- [x] **P1** Remove dead `_active_processes` registry from `CapabilitiesSystemJob` and simplify `cancel_job` (OR-1).
- [x] **P1** Rename `utility_version.py` → `utility_version_resolver.py` and update all imports (NM-1).
- [x] **P2** Refactor `SystemOrchestrator.execute_in_process` to a command dispatch-map pattern (SC-1).
- [x] **P3** Tighten `SystemConfigurationProtocol` signatures from `Any` to `str` (SC-4).
