"""System Agent Orchestrator — coordinates system lifecycle, workspace, and config capabilities."""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

from modules.shared.src.contract_registry_service_aggregate import (
    RegistryServiceAggregate,
)
from modules.shared.src.contract_system_configuration_protocol import (
    SystemConfigurationProtocol,
)
from modules.shared.src.contract_system_job_protocol import SystemJobProtocol
from modules.shared.src.contract_workspace_protocol import WorkspaceProtocol
from modules.shared.src.taxonomy_vision_vo import (
    CommandName,
    CommandOutput,
    ConfigKey,
    FilePath,
)


class SystemOrchestrator(RegistryServiceAggregate):
    """Orchestrator for system domain (pure delegation facade)."""

    def __init__(
        self,
        workspace: WorkspaceProtocol,
        config: SystemConfigurationProtocol,
        job: SystemJobProtocol,
    ) -> None:
        self._workspace = workspace
        self._config = config
        self._job = job

        # Dispatch map: command name -> handler(kwargs) -> CommandOutput
        self._handlers: dict[str, Callable[[dict[str, Any]], CommandOutput]] = {
            "init": self._handle_init,
            "get-config": self._handle_get_config,
            "config": self._handle_get_config,
            "set-config": self._handle_set_config,
            "status": self._handle_status,
            "cancel": self._handle_cancel,
        }

    def execute_in_process(
        self,
        command: CommandName,
        kwargs: dict[str, Any],
    ) -> CommandOutput:
        """Execute system commands by delegating to injected capabilities."""
        handler = self._handlers.get(command.value)
        if handler is None:
            raise ValueError(f"Unknown system command: {command.value}")
        return handler(kwargs)

    # ─── Private command handlers ─────────────────────────────

    def _handle_init(self, kwargs: dict[str, Any]) -> CommandOutput:
        target_val = kwargs.get("target_dir", ".") or "."
        target = FilePath(value=str(target_val))
        result = self._workspace.init_workspace(target)
        return CommandOutput(value=json.dumps(result, indent=2))

    def _handle_get_config(self, kwargs: dict[str, Any]) -> CommandOutput:
        key_val = str(kwargs.get("key", "") or "")
        result = self._config.get_config(key=ConfigKey(value=key_val) if key_val else None)
        return CommandOutput(value=json.dumps(result, indent=2))

    def _handle_set_config(self, kwargs: dict[str, Any]) -> CommandOutput:
        key_val = str(kwargs.get("key", ""))
        val = kwargs.get("value")
        result = self._config.set_config(ConfigKey(value=key_val), val)
        return CommandOutput(value=json.dumps(result, indent=2))

    def _handle_status(self, kwargs: dict[str, Any]) -> CommandOutput:
        _ = kwargs
        result = self._job.get_status()
        return CommandOutput(value=json.dumps(result, indent=2))

    def _handle_cancel(self, kwargs: dict[str, Any]) -> CommandOutput:
        job_id = str(kwargs.get("job_id", "") or "")
        result = self._job.cancel_job(job_id)
        return CommandOutput(value=json.dumps(result, indent=2))


__all__ = ["SystemOrchestrator"]
