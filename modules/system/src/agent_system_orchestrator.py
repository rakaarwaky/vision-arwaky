"""System Agent Orchestrator — coordinates system lifecycle, workspace, and config capabilities."""

import json
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
    FilePath,
)


class SystemOrchestrator(RegistryServiceAggregate):
    """Orchestrator for system domain (pure delegation facade)."""

    def __init__(
        self,
        workspace: WorkspaceProtocol,
        config: SystemConfigurationProtocol,
        job: SystemJobProtocol,
    ):
        self._workspace = workspace
        self._config = config
        self._job = job

    def execute_in_process(
        self,
        command: CommandName,
        kwargs: dict[str, Any],
    ) -> CommandOutput:
        """Execute system commands by delegating to injected capabilities."""
        if command.value == "init":
            target_val = kwargs.get("target_dir", ".") or "."
            target = FilePath(value=str(target_val))
            result = self._workspace.init_workspace(target)
            return CommandOutput(value=json.dumps(result, indent=2))
        if command.value in ("get-config", "config"):
            key_val = str(kwargs.get("key", "") or "")
            result = self._config.get_config(key=key_val)
            return CommandOutput(value=json.dumps(result, indent=2))
        if command.value == "set-config":
            key_val = str(kwargs.get("key", ""))
            val = kwargs.get("value")
            result = self._config.set_config(key_val, val)
            return CommandOutput(value=json.dumps(result, indent=2))
        if command.value == "status":
            result = self._job.get_status()
            return CommandOutput(value=json.dumps(result, indent=2))
        if command.value == "cancel":
            job_id = str(kwargs.get("job_id", "") or "")
            result = self._job.cancel_job(job_id)
            return CommandOutput(value=json.dumps(result, indent=2))
        raise ValueError(f"Unknown system command: {command.value}")


__all__ = ["SystemOrchestrator"]
