"""Unit tests for XDG Base Directory paths."""

from modules.shared.src.taxonomy_xdg_paths_vo import APP_NAME, XDGPaths


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
