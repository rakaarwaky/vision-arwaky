"""Unit tests for MCP surface handlers."""

import json

import pytest

from modules.mcp.src.surface_mcp_command import (
    vision_doctor,
    vision_image,
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


class _MockDispatcher(IRegistryServiceAggregate):
    """Minimal mock dispatcher that captures the last command and kwargs."""

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


class _FailingDispatcher(IRegistryServiceAggregate):
    """Dispatcher that raises on every call."""

    def execute_in_process(
        self,
        command: CommandName,
        kwargs: dict | SystemCommandParams,
    ) -> CommandOutput:
        raise ValueError("boom")


class TestMCPSurface:
    def test_image_dispatch(self):
        import modules.mcp.src.surface_mcp_command as surf

        dispatcher = _MockDispatcher()
        dispatcher._result = CommandOutput(value=json.dumps({"image_analysis": "ok"}))
        surf._dispatcher = dispatcher

        result = json.loads(vision_image(image="test.png", prompt="describe"))
        assert result["image_analysis"] == "ok"
        assert dispatcher.last_cmd is not None
        assert dispatcher.last_cmd.value == "analyze"
        kwargs = dispatcher.last_kwargs
        assert kwargs is not None
        if isinstance(kwargs, dict):
            assert kwargs["image"] == "test.png"
            assert kwargs["prompt"] == "describe"
        surf._dispatcher = None

    def test_video_dispatch(self):
        import modules.mcp.src.surface_mcp_command as surf

        dispatcher = _MockDispatcher()
        dispatcher._result = CommandOutput(value=json.dumps({"video_analysis": "ok"}))
        surf._dispatcher = dispatcher

        result = json.loads(vision_video(video="test.mp4"))
        assert result["video_analysis"] == "ok"
        assert dispatcher.last_cmd is not None
        assert dispatcher.last_cmd.value == "analyze-video"
        kwargs = dispatcher.last_kwargs
        assert kwargs is not None
        if isinstance(kwargs, dict):
            assert kwargs["video"] == "test.mp4"
        surf._dispatcher = None

    def test_doctor_dispatch(self):
        import modules.mcp.src.surface_mcp_command as surf

        dispatcher = _MockDispatcher()
        dispatcher._result = CommandOutput(
            value=json.dumps(
                {"ready": True, "version": "v3.0.0", "checks": {}, "failed": []}
            )
        )
        surf._dispatcher = dispatcher

        result = json.loads(vision_doctor())
        assert result["ready"] is True
        assert "version" in result
        surf._dispatcher = None

    def test_dispatch_no_dispatcher_raises(self, monkeypatch):
        monkeypatch.setattr("modules.mcp.src.surface_mcp_command._dispatcher", None)
        with pytest.raises(RuntimeError):
            vision_image(image="test.png")
        with pytest.raises(RuntimeError):
            vision_video(video="test.mp4")
        with pytest.raises(RuntimeError):
            vision_doctor()

    def test_dispatch_propagates_exception(self, monkeypatch):
        monkeypatch.setattr(
            "modules.mcp.src.surface_mcp_command._dispatcher",
            _FailingDispatcher(),
        )
        with pytest.raises(ValueError, match="boom"):
            vision_image(image="test.png")
        with pytest.raises(ValueError, match="boom"):
            vision_video(video="test.mp4")
        with pytest.raises(ValueError, match="boom"):
            vision_doctor()
