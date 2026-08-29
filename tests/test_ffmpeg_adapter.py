import asyncio

import pytest

from modules.video.src.capabilities_ffmpeg_adapter import FFmpegVideoAdapter


class FakeProcess:
    def __init__(self):
        self.returncode = 0
        self.killed = False
        self.waited = False

    async def communicate(self):
        return b"ffmpeg output", b""

    def kill(self):
        self.killed = True

    async def wait(self):
        self.waited = True


def test_ffmpeg_uses_devnull_stdin(monkeypatch):
    calls = []
    process = FakeProcess()

    async def fake_create_subprocess_exec(*args, **kwargs):
        calls.append((args, kwargs))
        return process

    monkeypatch.setattr(asyncio, "create_subprocess_exec", fake_create_subprocess_exec)

    result = asyncio.run(FFmpegVideoAdapter().run(["-version"], timeout=3))

    assert result == "ffmpeg output"
    assert calls[0][1]["stdin"] is asyncio.subprocess.DEVNULL
    assert process.killed is False
    assert process.waited is False


def test_ffmpeg_timeout_kills_and_waits_for_process(monkeypatch):
    process = FakeProcess()

    async def fake_create_subprocess_exec(*args, **kwargs):
        return process

    async def fake_wait_for(awaitable, timeout):
        awaitable.close()
        raise TimeoutError

    monkeypatch.setattr(asyncio, "create_subprocess_exec", fake_create_subprocess_exec)
    monkeypatch.setattr(asyncio, "wait_for", fake_wait_for)

    with pytest.raises(RuntimeError, match=r"FFmpeg timed out after 2s"):
        asyncio.run(FFmpegVideoAdapter().run(["-version"], timeout=2))

    assert process.killed is True
    assert process.waited is True


def test_ffmpeg_rejects_non_positive_timeout():
    with pytest.raises(ValueError, match="greater than zero"):
        asyncio.run(FFmpegVideoAdapter().run(["-version"], timeout=0))
