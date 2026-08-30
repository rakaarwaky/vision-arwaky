"""Unit tests for CapabilitiesSystemJob (FR-SYS-003)."""

from modules.system.src.capabilities_system_job import CapabilitiesSystemJob


class TestSystemJob:
    """Test system job status and cancellation."""

    def test_get_status(self):
        job_cap = CapabilitiesSystemJob()
        status = job_cap.get_status()

        assert "server" in status
        assert "dependencies" in status
        assert "capabilities" in status
        assert "active_jobs" in status
        assert status["active_jobs"] == 0

    def test_cancel_job_empty(self):
        job_cap = CapabilitiesSystemJob()
        res = job_cap.cancel_job()

        assert res["active_jobs"] == 0
        assert res["supported"] is False
