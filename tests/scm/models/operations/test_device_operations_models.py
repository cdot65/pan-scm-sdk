"""Tests for device operations models."""

import pytest
from pydantic import ValidationError

from scm.models.operations.device_operations import (
    DeviceJobDetailsModel,
    DeviceJobResultModel,
    DeviceJobStatusModel,
    DeviceOperationsRequestModel,
    JobCreatedModel,
)


class TestDeviceOperationsRequestModel:
    def test_valid_single_device(self):
        model = DeviceOperationsRequestModel(devices=["007951000123456"])
        assert len(model.devices) == 1

    def test_valid_five_devices(self):
        devices = [f"00795100012345{i}" for i in range(5)]
        model = DeviceOperationsRequestModel(devices=devices)
        assert len(model.devices) == 5

    def test_empty_devices_rejected(self):
        with pytest.raises(ValidationError):
            DeviceOperationsRequestModel(devices=[])

    def test_too_many_devices_rejected(self):
        devices = [f"00795100012345{i}" for i in range(6)]
        with pytest.raises(ValidationError):
            DeviceOperationsRequestModel(devices=devices)

    def test_invalid_serial_format_rejected(self):
        with pytest.raises(ValidationError):
            DeviceOperationsRequestModel(devices=["abc"])

    def test_valid_14_digit_serial(self):
        model = DeviceOperationsRequestModel(devices=["00795100012345"])
        assert model.devices[0] == "00795100012345"

    def test_valid_15_digit_serial(self):
        model = DeviceOperationsRequestModel(devices=["007951000123456"])
        assert model.devices[0] == "007951000123456"


class TestJobCreatedModel:
    def test_valid_job_id(self):
        model = JobCreatedModel(job_id="550e8400-e29b-41d4-a716-446655440000")
        assert model.job_id == "550e8400-e29b-41d4-a716-446655440000"


class TestDeviceJobDetailsModel:
    def test_valid_details(self):
        model = DeviceJobDetailsModel(
            msg="Command completed successfully.",
            result={"router_global": {"3.3.3.3/32": [{"prefix": "3.3.3.3/32"}]}},
        )
        assert model.msg == "Command completed successfully."
        assert "router_global" in model.result

    def test_empty_result(self):
        model = DeviceJobDetailsModel(msg="Pending.", result={})
        assert model.result == {}


class TestDeviceJobResultModel:
    def test_valid_result(self):
        model = DeviceJobResultModel(
            device="007951000123456",
            state="complete",
            created_ts="2026-03-02 19:00:04",
            updated_ts="2026-03-02 19:00:04",
            details={"msg": "Command completed successfully.", "result": {}},
        )
        assert model.device == "007951000123456"
        assert model.state == "complete"
        assert model.details.msg == "Command completed successfully."

    def test_valid_states(self):
        for state in ["pending", "in_progress", "complete", "failed"]:
            model = DeviceJobResultModel(
                device="007951000123456",
                state=state,
                created_ts="2026-03-02 19:00:04",
                updated_ts="2026-03-02 19:00:04",
                details={"msg": "test", "result": {}},
            )
            assert model.state == state


class TestDeviceJobStatusModel:
    def test_valid_complete_job(self):
        model = DeviceJobStatusModel(
            jobId="ab123c4d-e56f-7g8h-901i-23jk4l5mn678",
            progress=100,
            state="complete",
            request={"command": "show-advanced-routing-route", "devices": ["007951000123456"]},
            results=[
                {
                    "device": "007951000123456",
                    "state": "complete",
                    "created_ts": "2026-03-02 19:00:04",
                    "updated_ts": "2026-03-02 19:00:04",
                    "details": {"msg": "Command completed successfully.", "result": {}},
                }
            ],
        )
        assert model.jobId == "ab123c4d-e56f-7g8h-901i-23jk4l5mn678"
        assert model.progress == 100
        assert model.state == "complete"
        assert len(model.results) == 1

    def test_in_progress_job(self):
        model = DeviceJobStatusModel(
            jobId="test-job-id",
            progress=50,
            state="in_progress",
            request={"command": "show-advanced-routing-route", "devices": ["007951000123456"]},
            results=[],
        )
        assert model.progress == 50
        assert model.state == "in_progress"
        assert len(model.results) == 0

    def test_progress_bounds(self):
        with pytest.raises(ValidationError):
            DeviceJobStatusModel(
                jobId="test", progress=-1, state="pending",
                request={"command": "test", "devices": ["007951000123456"]}, results=[],
            )
        with pytest.raises(ValidationError):
            DeviceJobStatusModel(
                jobId="test", progress=101, state="pending",
                request={"command": "test", "devices": ["007951000123456"]}, results=[],
            )
