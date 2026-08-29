"""System container — Dependency injection root for system domain."""

from typing import TypedDict

from modules.shared.src.contract_system_configuration_protocol import (
    SystemConfigurationProtocol,
)
from modules.shared.src.contract_system_job_protocol import SystemJobProtocol
from modules.shared.src.contract_workspace_protocol import WorkspaceProtocol
from modules.system.src.agent_system_orchestrator import SystemOrchestrator
from modules.system.src.capabilities_system_configuration import (
    CapabilitiesSystemConfiguration,
)
from modules.system.src.capabilities_system_job import CapabilitiesSystemJob
from modules.system.src.capabilities_system_workspace import (
    CapabilitiesSystemWorkspace,
)


def build_system_workspace() -> CapabilitiesSystemWorkspace:
    """Instantiate System Workspace capability."""
    return CapabilitiesSystemWorkspace()


def build_system_configuration() -> CapabilitiesSystemConfiguration:
    """Instantiate System Configuration capability."""
    return CapabilitiesSystemConfiguration()


def build_system_job() -> CapabilitiesSystemJob:
    """Instantiate System Job capability."""
    return CapabilitiesSystemJob()


def build_system_orchestrator(
    workspace_port: CapabilitiesSystemWorkspace,
    config_port: CapabilitiesSystemConfiguration,
    job_port: CapabilitiesSystemJob,
) -> SystemOrchestrator:
    """Instantiate System Agent Orchestrator with injected capability ports."""
    return SystemOrchestrator(
        workspace=workspace_port,
        config=config_port,
        job=job_port,
    )


class SystemFeature(TypedDict):
    workspace: WorkspaceProtocol
    config: SystemConfigurationProtocol
    job: SystemJobProtocol
    system_orchestrator: SystemOrchestrator


class SystemContainer:
    """Composition root for the system domain."""

    def __init__(
        self,
        workspace_port: CapabilitiesSystemWorkspace | None = None,
        config_port: CapabilitiesSystemConfiguration | None = None,
        job_port: CapabilitiesSystemJob | None = None,
        orchestrator: SystemOrchestrator | None = None,
    ) -> None:
        self._workspace = workspace_port or build_system_workspace()
        self._config = config_port or build_system_configuration()
        self._job = job_port or build_system_job()
        self._orchestrator = orchestrator or build_system_orchestrator(
            self._workspace,
            self._config,
            self._job,
        )

    @property
    def orchestrator(self) -> SystemOrchestrator:
        """Return the wired System Agent Orchestrator."""
        return self._orchestrator

    @property
    def workspace(self) -> CapabilitiesSystemWorkspace:
        """Return the Workspace capability."""
        return self._workspace

    @property
    def config(self) -> CapabilitiesSystemConfiguration:
        """Return the Configuration capability."""
        return self._config

    @property
    def job(self) -> CapabilitiesSystemJob:
        """Return the Job capability."""
        return self._job


def build_system_feature() -> SystemFeature:
    """Build the concrete capability ports and orchestrator for the system domain."""
    container = SystemContainer()
    return {
        "workspace": container.workspace,
        "config": container.config,
        "job": container.job,
        "system_orchestrator": container.orchestrator,
    }


__all__ = [
    "SystemContainer",
    "SystemFeature",
    "build_system_configuration",
    "build_system_feature",
    "build_system_job",
    "build_system_orchestrator",
    "build_system_workspace",
]
