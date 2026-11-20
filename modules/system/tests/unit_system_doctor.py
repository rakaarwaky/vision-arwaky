"""Unit tests for CapabilitiesSystemDoctor (system readiness checks)."""

import json
from unittest.mock import patch

from modules.system.src.capabilities_system_doctor import CapabilitiesSystemDoctor


class TestSystemDoctor:
    """Test the doctor capability's readiness report structure."""

    def test_check_readiness_structure(self):
        doctor = CapabilitiesSystemDoctor()
        report = json.loads(doctor.check_readiness().value)

        assert "ready" in report
        assert "version" in report
        assert "checks" in report
        assert "failed" in report
        assert isinstance(report["ready"], bool)
        assert isinstance(report["checks"]["dependencies"], dict)
        assert isinstance(report["checks"]["capabilities"], dict)
        assert "image_analysis" in report["checks"]["capabilities"]
        assert "video_processing" in report["checks"]["capabilities"]
        assert "llm_vision" in report["checks"]["capabilities"]

    def test_check_readiness_ready_true_when_all_pass(self):
        with (
            patch(
                "modules.system.src.capabilities_system_doctor.check_all_dependencies",
                return_value={
                    "opencv": "OK",
                    "numpy": "OK",
                    "requests": "OK",
                    "pyyaml": "OK",
                    "ffmpeg": "OK",
                    "ffprobe": "OK",
                },
            ),
            patch(
                "modules.system.src.capabilities_system_doctor.resolve_external_settings",
                return_value=("http://localhost:8080", "key", "model"),
            ),
            patch(
                "modules.system.src.capabilities_system_doctor.check_llm_endpoint",
                return_value=(True, "OK"),
            ),
            patch(
                "modules.system.src.capabilities_system_doctor.find_active_config",
                return_value=None,
            ),
            patch(
                "modules.system.src.capabilities_system_doctor.get_package_version",
                return_value="3.0.0",
            ),
        ):
            doctor = CapabilitiesSystemDoctor()
            report = json.loads(doctor.check_readiness().value)

        assert report["ready"] is True
        assert report["failed"] == []
        assert report["checks"]["capabilities"]["image_analysis"] is True
        assert report["checks"]["capabilities"]["video_processing"] is True
        assert report["checks"]["capabilities"]["llm_vision"] is True

    def test_check_readiness_ready_false_when_llm_missing(self):
        with (
            patch(
                "modules.system.src.capabilities_system_doctor.check_all_dependencies",
                return_value={
                    "opencv": "OK",
                    "numpy": "OK",
                    "requests": "OK",
                    "pyyaml": "OK",
                    "ffmpeg": "MISSING",
                    "ffprobe": "MISSING",
                },
            ),
            patch(
                "modules.system.src.capabilities_system_doctor.resolve_external_settings",
                return_value=("http://localhost:8080", "", ""),
            ),
            patch(
                "modules.system.src.capabilities_system_doctor.check_llm_endpoint",
                return_value=(False, "UNREACHABLE"),
            ),
            patch(
                "modules.system.src.capabilities_system_doctor.find_active_config",
                return_value=None,
            ),
            patch(
                "modules.system.src.capabilities_system_doctor.get_package_version",
                return_value="3.0.0",
            ),
        ):
            doctor = CapabilitiesSystemDoctor()
            report = json.loads(doctor.check_readiness().value)

        assert report["ready"] is False
        assert "llm_endpoint" in report["failed"]
        assert report["checks"]["capabilities"]["video_processing"] is False
