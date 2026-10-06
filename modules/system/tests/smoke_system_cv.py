"""Smoke tests: system container boots and responds fast (FR-SYS-002)."""

import time

from modules.shared.src.taxonomy_vision_vo import (
    CommandName,
    SystemCommandParams,
)
from modules.system.src.root_system_container import SystemContainer


class TestSystemSmoke:
    def test_container_boots_under_one_second(self):
        start = time.monotonic()
        container = SystemContainer()
        elapsed = time.monotonic() - start
        assert container.orchestrator is not None
        assert elapsed < 1.0

    def test_status_responds_fast(self):
        container = SystemContainer()
        start = time.monotonic()
        out = container.orchestrator.execute_in_process(
            CommandName(value="status"),
            SystemCommandParams(),
        )
        assert out.value is not None
        assert time.monotonic() - start < 0.5
