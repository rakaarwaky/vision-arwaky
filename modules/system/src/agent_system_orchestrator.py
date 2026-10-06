"""System Agent Orchestrator — coordinates system lifecycle, workspace, and config capabilities."""

from __future__ import annotations

from collections.abc import Callable

from modules.shared.src.contract_registry_service_aggregate import (
    IRegistryServiceAggregate,
)
from modules.shared.src.contract_system_configuration_protocol import (
    ISystemConfigurationProtocol,
)
from modules.shared.src.contract_system_job_protocol import ISystemJobProtocol
from modules.shared.src.contract_workspace_protocol import IWorkspaceProtocol
from modules.shared.src.taxonomy_vision_error import InvalidParameterError
from modules.shared.src.taxonomy_vision_vo import (
    CommandName,
    CommandOutput,
    ConfigKey,
    FilePath,
    SystemCommandParams,
)
from modules.shared.src.utility_command_output import dict_to_command_output


class SystemOrchestrator(IRegistryServiceAggregate):
    """Orchestrator for system domain (pure delegation facade)."""

    def __init__(
        self,
        workspace: IWorkspaceProtocol,
        config: ISystemConfigurationProtocol,
        job: ISystemJobProtocol,
    ) -> None:
        self._workspace = workspace
        self._config = config
        self._job = job

        # Dispatch map: command name -> handler(params) -> CommandOutput
        self._handlers: dict[
            str,
            Callable[[SystemCommandParams], CommandOutput],
        ] = {
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
        params: SystemCommandParams | dict,
    ) -> CommandOutput:
        """Execute system commands by delegating to injected capabilities."""
        if isinstance(params, dict):
            params = SystemCommandParams(**params)
        handler = self._handlers.get(command.value)
        if handler is None:
            raise InvalidParameterError(f"Unknown system command: {command.value}")
        return handler(params)

    # ─── Private command handlers ─────────────────────────────

    def _handle_init(self, params: SystemCommandParams) -> CommandOutput:
        target_val = str(params.model_dump().get("target_dir", ".") or ".")
        target = FilePath.from_str(target_val)
        result = self._workspace.init_workspace(target)
        return dict_to_command_output(result)

    def _handle_get_config(self, params: SystemCommandParams) -> CommandOutput:
        key_val = str(params.model_dump().get("key", "") or "")
        result = self._config.get_config(
            key=ConfigKey(value=key_val) if key_val else None
        )
        return dict_to_command_output(result)

    def _handle_set_config(self, params: SystemCommandParams) -> CommandOutput:
        data = params.model_dump()
        key_val = str(data.get("key", ""))
        val = data.get("value")
        result = self._config.set_config(ConfigKey(value=key_val), val)
        return dict_to_command_output(result)

    def _handle_status(self, params: SystemCommandParams) -> CommandOutput:
        _ = params
        result = self._job.get_status()
        return dict_to_command_output(result)

    def _handle_cancel(self, params: SystemCommandParams) -> CommandOutput:
        job_id = str(params.model_dump().get("job_id", "") or "")
        result = self._job.cancel_job(job_id)
        return dict_to_command_output(result)


__all__ = ["SystemOrchestrator"]
