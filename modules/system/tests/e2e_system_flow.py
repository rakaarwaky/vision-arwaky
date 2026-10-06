"""E2E tests: full system request lifecycle through the orchestrator."""

import json

from modules.shared.src.taxonomy_vision_vo import (
    CommandName,
    SystemCommandParams,
)
from modules.system.src.root_system_container import SystemContainer


class TestSystemE2E:
    def test_get_config_lifecycle(self):
        container = SystemContainer()
        out = container.orchestrator.execute_in_process(
            CommandName(value="get-config"),
            SystemCommandParams(key=""),
        )
        payload = json.loads(out.value)
        assert isinstance(payload, dict)

    def test_unknown_command_is_controlled_error(self):
        container = SystemContainer()
        try:
            container.orchestrator.execute_in_process(
                CommandName(value="bogus"),
                SystemCommandParams(),
            )
            assert False, "expected controlled ValueError"
        except ValueError:
            pass
