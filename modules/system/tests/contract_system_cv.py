"""Contract tests: system feature implements shared protocols and aggregate."""

import inspect

from modules.shared.src.contract_registry_service_aggregate import (
    IRegistryServiceAggregate,
)
from modules.shared.src.contract_system_configuration_protocol import (
    ISystemConfigurationProtocol,
)
from modules.shared.src.contract_system_job_protocol import ISystemJobProtocol
from modules.shared.src.contract_workspace_protocol import IWorkspaceProtocol
from modules.system.src.agent_system_orchestrator import SystemOrchestrator
from modules.system.src.capabilities_system_configuration import (
    CapabilitiesSystemConfiguration,
)
from modules.system.src.capabilities_system_job import CapabilitiesSystemJob
from modules.system.src.capabilities_system_workspace import (
    CapabilitiesSystemWorkspace,
)


class TestSystemContracts:
    def test_workspace_implements_protocol(self):
        assert issubclass(CapabilitiesSystemWorkspace, IWorkspaceProtocol)

    def test_configuration_implements_protocol(self):
        assert issubclass(CapabilitiesSystemConfiguration, ISystemConfigurationProtocol)

    def test_job_implements_protocol(self):
        assert issubclass(CapabilitiesSystemJob, ISystemJobProtocol)

    def test_orchestrator_implements_aggregate(self):
        assert issubclass(SystemOrchestrator, IRegistryServiceAggregate)

    def test_configuration_public_methods_present(self):
        methods = {
            name
            for name, _ in inspect.getmembers(
                CapabilitiesSystemConfiguration, inspect.isfunction
            )
            if not name.startswith("_")
        }
        assert "get_config" in methods
        assert "set_config" in methods

    def test_protocol_abstract_methods_respected(self):
        abstract = set(
            getattr(ISystemConfigurationProtocol, "__abstractmethods__", set())
        )
        assert "get_config" in abstract
        assert "set_config" in abstract
