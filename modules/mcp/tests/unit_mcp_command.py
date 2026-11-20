"""Unit tests for MCP action functions (vision_init, vision_image, vision_video, vision_doctor)."""

import json
from pathlib import Path

from modules.mcp.src.surface_mcp_command import (
    set_mcp_dispatcher,
    vision_doctor,
    vision_image,
    vision_init,
    vision_video,
)
from modules.shared.src.common.taxonomy_vision_vo import (
    CommandName,
    CommandOutput,
    SystemCommandParams,
)
from modules.shared.src.contract_registry_service_aggregate import (
    IRegistryServiceAggregate,
)
from modules.system.src.root_system_container import SystemContainer


class _MockDispatcher(IRegistryServiceAggregate):
    """Captures the last command and kwargs for inspection."""

    def __init__(self) -> None:
        self._result = CommandOutput(value=json.dumps({"mock": True}))
        self.last_cmd: CommandName | None = None
        self.last_kwargs: dict | SystemCommandParams | None = None

    def execute_in_process(
        self,
        command: CommandName,
        kwargs: dict | SystemCommandParams,
    ) -> CommandOutput:
        self.last_cmd = command
        self.last_kwargs = kwargs
        return self._result


class TestMCPActions:
    def test_vision_init(self, tmp_path: Path):
        set_mcp_dispatcher(SystemContainer().orchestrator)
        result_raw = vision_init(target_dir=str(tmp_path))
        data = json.loads(result_raw)
        assert "xdg_config" in data
        assert (tmp_path / ".vision-arwaky").exists()

    def test_vision_image_dispatch(self, tmp_path: Path):
        mock = _MockDispatcher()
        mock._result = CommandOutput(value=json.dumps({"image_analysis": "ok"}))
        set_mcp_dispatcher(mock)

        result = vision_image(image=str(tmp_path / "test.png"), prompt="hi")
        assert json.loads(result)["image_analysis"] == "ok"
        assert mock.last_cmd is not None
        assert mock.last_cmd.value == "analyze"
        kwargs = mock.last_kwargs
        assert kwargs is not None
        if isinstance(kwargs, dict):
            assert kwargs["image"] == str(tmp_path / "test.png")
            assert kwargs["prompt"] == "hi"

    def test_vision_video_dispatch(self, tmp_path: Path):
        mock = _MockDispatcher()
        mock._result = CommandOutput(value=json.dumps({"video_analysis": "ok"}))
        set_mcp_dispatcher(mock)

        result = vision_video(video=str(tmp_path / "test.mp4"))
        assert json.loads(result)["video_analysis"] == "ok"
        assert mock.last_cmd is not None
        assert mock.last_cmd.value == "analyze-video"
        kwargs = mock.last_kwargs
        assert kwargs is not None
        if isinstance(kwargs, dict):
            assert kwargs["video"] == str(tmp_path / "test.mp4")

    def test_vision_doctor_dispatch(self):
        mock = _MockDispatcher()
        set_mcp_dispatcher(mock)
        result = vision_doctor()
        data = json.loads(result)
        assert "mock" in data
