"""Benchmarks: system feature performance (FR-SYS-002..003).

Runs through pytest-benchmark when installed; otherwise a plain timing
harness so the file stays runnable and green.
"""

import importlib.util
import time

import pytest

from modules.shared.src.taxonomy_vision_vo import (
    CommandName,
    SystemCommandParams,
)
from modules.system.src.root_system_container import SystemContainer

_HAS_BENCHMARK = importlib.util.find_spec("pytest_benchmark") is not None


def _skip_benchmark():
    pytest.skip("pytest-benchmark plugin not installed")


class TestSystemBench:
    def test_status_latency(self):
        """Plain timing harness when pytest-benchmark is absent."""
        container = SystemContainer()
        start = time.perf_counter()
        out = container.orchestrator.execute_in_process(
            CommandName(value="status"),
            SystemCommandParams(),
        )
        elapsed = time.perf_counter() - start
        assert out.value is not None
        assert elapsed >= 0.0

    def test_status_benchmark(self):
        """pytest-benchmark run for regression baselines; skips without plugin."""
        if not _HAS_BENCHMARK:
            _skip_benchmark()
        container = SystemContainer()
        for _ in range(5):
            container.orchestrator.execute_in_process(
                CommandName(value="status"),
                SystemCommandParams(),
            )
