"""Unit tests for CapabilitiesSystemConfiguration (FR-SYS-002)."""

from pathlib import Path

from modules.system.src.capabilities_system_configuration import (
    CapabilitiesSystemConfiguration,
)


class TestSystemConfiguration:
    """Test reading and overwriting configuration."""

    def test_get_config_empty(self, tmp_path: Path):
        cfg_file = tmp_path / "user_config.yaml"
        local_cfg = tmp_path / "local_config.yaml"
        cap = CapabilitiesSystemConfiguration(
            config_path=cfg_file, local_config_path=local_cfg
        )
        assert cap.get_config() == {}

    def test_set_and_get_config(self, tmp_path: Path):
        cfg_file = tmp_path / "user_config.yaml"
        local_cfg = tmp_path / "local_config.yaml"
        cap = CapabilitiesSystemConfiguration(
            config_path=cfg_file, local_config_path=local_cfg
        )

        res = cap.set_config("external.url", "http://localhost:8000/v1")
        assert res["status"] == "updated"
        assert res["value"] == "http://localhost:8000/v1"

        # Read back
        assert cap.get_config("external.url") == "http://localhost:8000/v1"
        full = cap.get_config()
        assert full.get("external", {}).get("url") == "http://localhost:8000/v1"
