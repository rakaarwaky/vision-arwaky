"""System container — Dependency injection root for system domain."""

from typing import TypedDict

from modules.shared.src.contract_registry_service_aggregate import (
    IRegistryServiceAggregate,
)
from modules.shared.src.system.contract_system_configuration_protocol import (
    ISystemConfigurationProtocol,
)
from modules.shared.src.system.contract_system_doctor_protocol import (
    ISystemDoctorProtocol,
)
from modules.shared.src.system.contract_system_job_protocol import ISystemJobProtocol
from modules.shared.src.system.contract_workspace_protocol import IWorkspaceProtocol
from modules.system.src.agent_system_orchestrator import SystemOrchestrator
from modules.system.src.capabilities_system_configuration import (
    CapabilitiesSystemConfiguration,
)
from modules.system.src.capabilities_system_doctor import (
    CapabilitiesSystemDoctor,
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


def build_system_doctor() -> CapabilitiesSystemDoctor:
    """Instantiate System Doctor capability."""
    return CapabilitiesSystemDoctor()


def build_system_orchestrator(
    workspace_port: CapabilitiesSystemWorkspace,
    config_port: CapabilitiesSystemConfiguration,
    job_port: CapabilitiesSystemJob,
    doctor_port: CapabilitiesSystemDoctor | None = None,
) -> SystemOrchestrator:
    """Instantiate System Agent Orchestrator with injected capability ports."""
    doctor = doctor_port or build_system_doctor()
    return SystemOrchestrator(
        workspace=workspace_port,
        config=config_port,
        job=job_port,
        doctor=doctor,
    )


class SystemFeature(TypedDict):
    """Composition of system domain capability ports and orchestrator."""

    workspace: IWorkspaceProtocol
    config: ISystemConfigurationProtocol
    job: ISystemJobProtocol
    doctor: ISystemDoctorProtocol
    system_orchestrator: IRegistryServiceAggregate


class SystemContainer:
    """Composition root for the system domain."""

    def __init__(
        self,
        workspace_port: CapabilitiesSystemWorkspace | None = None,
        config_port: CapabilitiesSystemConfiguration | None = None,
        job_port: CapabilitiesSystemJob | None = None,
        doctor_port: CapabilitiesSystemDoctor | None = None,
        orchestrator: SystemOrchestrator | None = None,
    ) -> None:
        """Initialize the system domain container with optional injected ports."""
        self._workspace = workspace_port or build_system_workspace()
        self._config = config_port or build_system_configuration()
        self._job = job_port or build_system_job()
        self._doctor = doctor_port or build_system_doctor()
        self._orchestrator = orchestrator or build_system_orchestrator(
            self._workspace,
            self._config,
            self._job,
            doctor_port=self._doctor,
        )

    @property
    def orchestrator(self) -> IRegistryServiceAggregate:
        """Return the wired System Agent Orchestrator (as its aggregate seam)."""
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

    @property
    def doctor(self) -> ISystemDoctorProtocol:
        """Return the Doctor capability."""
        return self._doctor


def build_system_feature() -> SystemFeature:
    """Build the concrete capability ports and orchestrator for the system domain."""
    container = SystemContainer()
    return {
        "workspace": container.workspace,
        "config": container.config,
        "job": container.job,
        "doctor": container.doctor,
        "system_orchestrator": container.orchestrator,
    }


__all__ = [
    "SystemContainer",
    "SystemFeature",
    "build_system_configuration",
    "build_system_doctor",
    "build_system_feature",
    "build_system_job",
    "build_system_orchestrator",
    "build_system_workspace",
]
