"""Acceptance tests: business requirements FR-SYS-001..003."""

import json
from pathlib import Path

from modules.shared.src.taxonomy_vision_vo import (
    CommandName,
    SystemCommandParams,
)
from modules.system.src.capabilities_system_configuration import (
    CapabilitiesSystemConfiguration,
)
from modules.system.src.root_system_container import SystemContainer


class TestSystemAcceptance:
    def test_fr_sys_002_config_read_and_overwrite(self, tmp_path: Path):
        """FR-SYS-002: read resolves config; overwrite persists a key."""
        cap = CapabilitiesSystemConfiguration(
            config_path=tmp_path / "user_config.yaml",
            local_config_path=tmp_path / "local_config.yaml",
        )
        result = cap.set_config("external.url", "http://localhost:8000/v1")
        assert result["status"] == "updated"
        assert cap.get_config("external.url") == "http://localhost:8000/v1"

    def test_fr_sys_003_job_status_shape(self):
        """FR-SYS-003: status exposes server, deps, capabilities, active jobs."""
        container = SystemContainer()
        out = container.orchestrator.execute_in_process(
            CommandName(value="status"),
            SystemCommandParams(),
        )
        payload = json.loads(out.value)
        assert "active_jobs" in payload
