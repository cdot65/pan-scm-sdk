"""Tests for DeviceOperations service."""

from unittest.mock import MagicMock, patch

from pydantic import ValidationError
import pytest

from scm.exceptions import JobTimeoutError
from scm.models.operations.device_operations import (
    DeviceJobStatusModel,
    JobCreatedModel,
)
from scm.operations.device_operations import DeviceOperations


class TestDeviceOperations:
    """Tests for the DeviceOperations service."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock API client."""
        client = MagicMock()
        client.get = MagicMock()
        client.post = MagicMock()
        return client

    @pytest.fixture
    def device_ops(self, mock_client):
        """Create a DeviceOperations service instance with mock client."""
        return DeviceOperations(mock_client)

    def test_route_table_async(self, device_ops, mock_client):
        """Test that route_table dispatches async job correctly."""
        mock_client.post.return_value = {"job_id": "test-job-123"}
        result = device_ops.route_table(devices=["007951000123456"])
        mock_client.post.assert_called_once_with(
            "/operations/v1/jobs/route-table",
            json={"devices": ["007951000123456"]},
        )
        assert isinstance(result, JobCreatedModel)
        assert result.job_id == "test-job-123"

    def test_fib_table_async(self, device_ops, mock_client):
        """Test that fib_table dispatches async job correctly."""
        mock_client.post.return_value = {"job_id": "test-job-456"}
        result = device_ops.fib_table(devices=["007951000123456"])
        mock_client.post.assert_called_once_with(
            "/operations/v1/jobs/fib-table",
            json={"devices": ["007951000123456"]},
        )
        assert isinstance(result, JobCreatedModel)

    def test_dns_proxy_async(self, device_ops, mock_client):
        """Test that dns_proxy dispatches async job correctly."""
        mock_client.post.return_value = {"job_id": "test-job-789"}
        result = device_ops.dns_proxy(devices=["007951000123456"])
        mock_client.post.assert_called_once_with(
            "/operations/v1/jobs/dns-proxy",
            json={"devices": ["007951000123456"]},
        )
        assert isinstance(result, JobCreatedModel)

    def test_device_interfaces_async(self, device_ops, mock_client):
        """Test that device_interfaces dispatches async job correctly."""
        mock_client.post.return_value = {"job_id": "test-job-abc"}
        result = device_ops.device_interfaces(devices=["007951000123456"])
        mock_client.post.assert_called_once_with(
            "/operations/v1/jobs/device-interfaces",
            json={"devices": ["007951000123456"]},
        )
        assert isinstance(result, JobCreatedModel)

    def test_device_rules_async(self, device_ops, mock_client):
        """Test that device_rules dispatches async job correctly."""
        mock_client.post.return_value = {"job_id": "test-job-def"}
        result = device_ops.device_rules(devices=["007951000123456"])
        mock_client.post.assert_called_once_with(
            "/operations/v1/jobs/device-rules",
            json={"devices": ["007951000123456"]},
        )
        assert isinstance(result, JobCreatedModel)

    def test_bgp_policy_export_async(self, device_ops, mock_client):
        """Test that bgp_policy_export dispatches async job correctly."""
        mock_client.post.return_value = {"job_id": "test-job-ghi"}
        result = device_ops.bgp_policy_export(devices=["007951000123456"])
        mock_client.post.assert_called_once_with(
            "/operations/v1/jobs/bgp-policy-export",
            json={"devices": ["007951000123456"]},
        )
        assert isinstance(result, JobCreatedModel)

    def test_logging_service_status_async(self, device_ops, mock_client):
        """Test that logging_service_status dispatches async job correctly."""
        mock_client.post.return_value = {"job_id": "test-job-jkl"}
        result = device_ops.logging_service_status(devices=["007951000123456"])
        mock_client.post.assert_called_once_with(
            "/operations/v1/jobs/logging-service-forwarding-status",
            json={"devices": ["007951000123456"]},
        )
        assert isinstance(result, JobCreatedModel)

    def test_multiple_devices(self, device_ops, mock_client):
        """Test that multiple devices are sent in the request payload."""
        mock_client.post.return_value = {"job_id": "test-job-multi"}
        devices = ["007951000123456", "007951000123457", "007951000123458"]
        result = device_ops.route_table(devices=devices)
        call_args = mock_client.post.call_args
        assert call_args[1]["json"]["devices"] == devices
        assert isinstance(result, JobCreatedModel)

    def test_invalid_devices_rejected(self, device_ops):
        """Test that an empty devices list raises ValidationError."""
        with pytest.raises(ValidationError):
            device_ops.route_table(devices=[])

    def test_too_many_devices_rejected(self, device_ops):
        """Test that more than five devices raises ValidationError."""
        devices = [f"00795100012345{i}" for i in range(6)]
        with pytest.raises(ValidationError):
            device_ops.route_table(devices=devices)

    def test_invalid_serial_rejected(self, device_ops):
        """Test that an invalid serial format raises ValidationError."""
        with pytest.raises(ValidationError):
            device_ops.route_table(devices=["invalid"])

    def test_get_job_status(self, device_ops, mock_client):
        """Test that get_job_status returns parsed DeviceJobStatusModel."""
        mock_client.get.return_value = {
            "jobId": "test-job-123",
            "progress": 100,
            "state": "complete",
            "request": {"command": "show-advanced-routing-route", "devices": ["007951000123456"]},
            "results": [{
                "device": "007951000123456",
                "state": "complete",
                "created_ts": "2026-03-02 19:00:04",
                "updated_ts": "2026-03-02 19:00:04",
                "details": {"msg": "Command completed successfully.", "result": {}},
            }],
        }
        result = device_ops.get_job_status("test-job-123")
        mock_client.get.assert_called_once_with("/operations/v1/device/jobs/test-job-123")
        assert isinstance(result, DeviceJobStatusModel)
        assert result.state == "complete"
        assert result.progress == 100

    @patch("scm.operations.device_operations.time.sleep")
    def test_sync_mode_polls_until_complete(self, mock_sleep, device_ops, mock_client):
        """Test that sync mode polls until job state is complete."""
        mock_client.post.return_value = {"job_id": "test-job-sync"}
        mock_client.get.side_effect = [
            {
                "jobId": "test-job-sync", "progress": 50, "state": "in_progress",
                "request": {"command": "test", "devices": ["007951000123456"]},
                "results": [],
            },
            {
                "jobId": "test-job-sync", "progress": 100, "state": "complete",
                "request": {"command": "test", "devices": ["007951000123456"]},
                "results": [{
                    "device": "007951000123456", "state": "complete",
                    "created_ts": "2026-03-02 19:00:04", "updated_ts": "2026-03-02 19:00:04",
                    "details": {"msg": "Done.", "result": {}},
                }],
            },
        ]
        result = device_ops.route_table(devices=["007951000123456"], sync=True, poll_interval=1)
        assert isinstance(result, DeviceJobStatusModel)
        assert result.state == "complete"
        assert mock_client.get.call_count == 2
        mock_sleep.assert_called_once_with(1)

    @patch("scm.operations.device_operations.time.sleep")
    @patch("scm.operations.device_operations.time.time")
    def test_sync_mode_timeout(self, mock_time, mock_sleep, device_ops, mock_client):
        """Test that sync mode raises JobTimeoutError on timeout."""
        mock_client.post.return_value = {"job_id": "test-job-timeout"}
        mock_time.side_effect = [0, 0, 301]
        mock_client.get.return_value = {
            "jobId": "test-job-timeout", "progress": 50, "state": "in_progress",
            "request": {"command": "test", "devices": ["007951000123456"]},
            "results": [],
        }
        with pytest.raises(JobTimeoutError) as exc_info:
            device_ops.route_table(devices=["007951000123456"], sync=True, timeout=300)
        assert exc_info.value.job_id == "test-job-timeout"
        assert exc_info.value.last_state == "in_progress"

    @patch("scm.operations.device_operations.time.sleep")
    def test_sync_mode_failed_job(self, mock_sleep, device_ops, mock_client):
        """Test that sync mode returns failed status without raising."""
        mock_client.post.return_value = {"job_id": "test-job-fail"}
        mock_client.get.return_value = {
            "jobId": "test-job-fail", "progress": 100, "state": "failed",
            "request": {"command": "test", "devices": ["007951000123456"]},
            "results": [],
        }
        result = device_ops.route_table(devices=["007951000123456"], sync=True)
        assert isinstance(result, DeviceJobStatusModel)
        assert result.state == "failed"
