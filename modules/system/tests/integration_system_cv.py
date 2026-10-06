"""Integration tests: system DI container wiring (FR-SYS-001..003)."""

import json

from modules.shared.src.taxonomy_vision_vo import (
    CommandName,
    SystemCommandParams,
)
from modules.system.src.root_system_container import SystemContainer


class TestSystemDIWiring:
    def test_container_builds_all_ports(self):
        container = SystemContainer()
        assert container.orchestrator is not None
        assert container.workspace is not None
        assert container.config is not None
        assert container.job is not None

    def test_status_routes_through_job_port(self):
        container = SystemContainer()
        out = container.orchestrator.execute_in_process(
            CommandName(value="status"),
            SystemCommandParams(),
        )
        payload = json.loads(out.value)
        assert "server" in payload or "dependencies" in payload

    def test_unknown_command_is_controlled_error(self):
        container = SystemContainer()
        try:
            container.orchestrator.execute_in_process(
                CommandName(value="bogus-sys-cmd"),
                SystemCommandParams(),
            )
            assert False, "expected controlled ValueError"
        except ValueError:
            pass
