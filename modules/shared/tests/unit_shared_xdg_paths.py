"""Unit tests for XDG Base Directory paths."""

from modules.shared.src.taxonomy_xdg_paths_vo import APP_NAME, XDGPaths
from modules.shared.src.utility_xdg_paths import ensure_xdg_dirs


class TestXDGPaths:
    """Test Linux XDG Base Directory specification paths."""

    def test_xdg_app_name(self):
        assert APP_NAME == "vision-arwaky"

    def test_xdg_directory_paths(self):
        assert "vision-arwaky" in str(XDGPaths.config_dir())
        assert "vision-arwaky" in str(XDGPaths.data_dir())
        assert "vision-arwaky" in str(XDGPaths.cache_dir())
        assert "vision-arwaky" in str(XDGPaths.state_dir())
        assert "venv" in str(XDGPaths.venv_dir())

    def test_ensure_xdg_dirs(self, tmp_path, monkeypatch):
        monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
        monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "data"))
        monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))
        monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "state"))
        ensure_xdg_dirs()
        assert (tmp_path / "config" / APP_NAME).is_dir()
        assert (tmp_path / "data" / APP_NAME).is_dir()
        assert (tmp_path / "cache" / APP_NAME).is_dir()
        assert (tmp_path / "state" / APP_NAME).is_dir()
