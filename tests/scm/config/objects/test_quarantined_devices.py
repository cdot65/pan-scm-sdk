# tests/scm/config/objects/test_quarantined_devices.py

# Standard library imports
from unittest.mock import MagicMock

import pytest
from requests.exceptions import HTTPError

# Local SDK imports
from scm.config.objects import QuarantinedDevices
from scm.exceptions import InvalidObjectError, MissingQueryParameterError
from scm.models.objects import QuarantinedDevicesResponseModel
from tests.factories.objects.quarantined_devices import (
    QuarantinedDevicesCreateApiFactory,
    QuarantinedDevicesResponseFactory,
)


@pytest.mark.usefixtures("load_env")
class TestQuarantinedDevicesBase:
    """Base class for QuarantinedDevices tests."""

    @pytest.fixture(autouse=True)
    def setup_method(self, mock_scm):
        """Setup method that runs before each test."""
        self.mock_scm = mock_scm  # noqa
        self.mock_scm.get = MagicMock()
        self.mock_scm.post = MagicMock()
        self.mock_scm.delete = MagicMock()
        self.client = QuarantinedDevices(self.mock_scm)  # noqa


class TestQuarantinedDevicesList(TestQuarantinedDevicesBase):
    """Tests for listing Quarantined Devices."""

    def test_list_no_filters(self):
        """Test listing all quarantined devices without filters."""
        # Use the response factory to create consistent test data
        device1 = QuarantinedDevicesResponseFactory.build(
            host_id="host-1", serial_number="serial-1"
        )
        device2 = QuarantinedDevicesResponseFactory.build(
            host_id="host-2", serial_number="serial-2"
        )

        mock_response = [
            device1.model_dump(),
            device2.model_dump(),
        ]
        self.mock_scm.get.return_value = mock_response  # noqa

        result = self.client.list()

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/objects/v1/quarantined-devices",
            params={},
        )
        assert len(result) == 2
        assert result[0].host_id == "host-1"
        assert result[0].serial_number == "serial-1"
        assert result[1].host_id == "host-2"
        assert result[1].serial_number == "serial-2"

    def test_list_with_host_id_filter(self):
        """Test listing quarantined devices with host_id filter."""
        # Use the response factory to create consistent test data
        device = QuarantinedDevicesResponseFactory.build(
            host_id="filtered-host", serial_number="serial-123"
        )

        mock_response = [device.model_dump()]
        self.mock_scm.get.return_value = mock_response  # noqa

        result = self.client.list(host_id="filtered-host")

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/objects/v1/quarantined-devices",
            params={"host_id": "filtered-host"},
        )
        assert len(result) == 1
        assert result[0].host_id == "filtered-host"
        assert result[0].serial_number == "serial-123"

    def test_list_with_serial_number_filter(self):
        """Test listing quarantined devices with serial_number filter."""
        # Use the response factory to create consistent test data
        device = QuarantinedDevicesResponseFactory.build(
            host_id="host-123", serial_number="filtered-serial"
        )

        mock_response = [device.model_dump()]
        self.mock_scm.get.return_value = mock_response  # noqa

        result = self.client.list(serial_number="filtered-serial")

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/objects/v1/quarantined-devices",
            params={"serial_number": "filtered-serial"},
        )
        assert len(result) == 1
        assert result[0].host_id == "host-123"
        assert result[0].serial_number == "filtered-serial"

    def test_list_with_both_filters(self):
        """Test listing quarantined devices with both host_id and serial_number filters."""
        # Use the response factory to create consistent test data
        device = QuarantinedDevicesResponseFactory.build(
            host_id="specific-host", serial_number="specific-serial"
        )

        mock_response = [device.model_dump()]
        self.mock_scm.get.return_value = mock_response  # noqa

        result = self.client.list(host_id="specific-host", serial_number="specific-serial")

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/objects/v1/quarantined-devices",
            params={"host_id": "specific-host", "serial_number": "specific-serial"},
        )
        assert len(result) == 1
        assert result[0].host_id == "specific-host"
        assert result[0].serial_number == "specific-serial"

    def test_list_empty_response(self):
        """Test list with empty response."""
        self.mock_scm.get.return_value = []  # noqa

        result = self.client.list()

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/objects/v1/quarantined-devices",
            params={},
        )
        assert result == []

    def test_list_http_error(self):
        """Test error handling for list operation."""
        # Create a mock response to simulate an HTTP error
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            "_errors": [
                {
                    "code": "E001",
                    "message": "Unauthorized",
                    "details": {"errorType": "Invalid Authorization"},
                }
            ],
            "_request_id": "test-request-id",
        }
        mock_http_error = HTTPError(response=mock_response)
        self.mock_scm.get.side_effect = mock_http_error

        with pytest.raises(HTTPError) as excinfo:
            self.client.list()

        assert excinfo.value.response.status_code == 401
        self.mock_scm.get.assert_called_once_with(
            "/config/objects/v1/quarantined-devices",
            params={},
        )

    def test_list_invalid_response_format(self):
        """Test that InvalidObjectError is raised when API response is not a list."""
        # Mock the API to return a dictionary instead of a list
        self.mock_scm.get.return_value = {"invalid": "format"}

        # The list method should raise an InvalidObjectError
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.list()

        # Verify the error details
        assert "Invalid response format: expected list" in str(excinfo.value.message)
        assert excinfo.value.error_code == "E003"
        assert excinfo.value.http_status_code == 500

        # Verify the API was called correctly
        self.mock_scm.get.assert_called_once_with(
            "/config/objects/v1/quarantined-devices",
            params={},
        )


class TestQuarantinedDevicesCreate(TestQuarantinedDevicesBase):
    """Tests for creating Quarantined Devices."""

    def test_create_success(self):
        """Test successful creation of a quarantined device."""
        # Use the API factory to create consistent test data
        create_data = QuarantinedDevicesCreateApiFactory.build_complete()

        # Create a response model based on the create data
        response_model = QuarantinedDevicesResponseFactory.build(
            host_id=create_data["host_id"],
            serial_number=create_data["serial_number"],
        )

        self.mock_scm.post.return_value = response_model.model_dump()  # noqa

        result = self.client.create(create_data)

        self.mock_scm.post.assert_called_once_with(  # noqa
            "/config/objects/v1/quarantined-devices",
            json=create_data,
        )
        assert isinstance(result, QuarantinedDevicesResponseModel)
        assert result.host_id == create_data["host_id"]
        assert result.serial_number == create_data["serial_number"]

    def test_create_minimal_data(self):
        """Test creation with minimal required data."""
        # Use the API factory to create consistent test data with minimal fields
        create_data = QuarantinedDevicesCreateApiFactory.build_minimal()

        # Create a response model based on the create data
        response_model = QuarantinedDevicesResponseFactory.build(
            host_id=create_data["host_id"],
            serial_number=None,
        )

        self.mock_scm.post.return_value = response_model.model_dump()  # noqa

        result = self.client.create(create_data)

        self.mock_scm.post.assert_called_once_with(  # noqa
            "/config/objects/v1/quarantined-devices",
            json=create_data,
        )
        assert isinstance(result, QuarantinedDevicesResponseModel)
        assert result.host_id == create_data["host_id"]
        assert result.serial_number is None

    def test_create_missing_required_field(self):
        """Test that validation error is raised if host_id is missing."""
        with pytest.raises(ValueError) as excinfo:
            self.client.create({"serial_number": "serial-1"})

        assert "host_id" in str(excinfo.value)
        self.mock_scm.post.assert_not_called()  # noqa

    def test_create_http_error(self):
        """Test error handling for create operation."""
        # Use the API factory to create consistent test data
        create_data = QuarantinedDevicesCreateApiFactory.build_complete()

        # Create a mock response to simulate an HTTP error
        mock_response = MagicMock()
        mock_response.status_code = 409
        mock_response.json.return_value = {
            "_errors": [
                {
                    "code": "E004",
                    "message": "Conflict",
                    "details": {"errorType": "Device already quarantined"},
                }
            ],
            "_request_id": "test-request-id",
        }
        mock_http_error = HTTPError(response=mock_response)
        self.mock_scm.post.side_effect = mock_http_error

        with pytest.raises(HTTPError) as excinfo:
            self.client.create(create_data)

        assert excinfo.value.response.status_code == 409
        self.mock_scm.post.assert_called_once_with(
            "/config/objects/v1/quarantined-devices",
            json=create_data,
        )


class TestQuarantinedDevicesDelete(TestQuarantinedDevicesBase):
    """Tests for deleting Quarantined Devices."""

    def test_delete_success(self):
        """Test successful deletion of a quarantined device."""
        host_id = "host-to-delete"
        self.mock_scm.delete.return_value = None  # noqa

        self.client.delete(host_id)

        self.mock_scm.delete.assert_called_once_with(  # noqa
            "/config/objects/v1/quarantined-devices",
            params={"host_id": host_id},
        )

    def test_delete_empty_host_id(self):
        """Test that MissingQueryParameterError is raised if host_id is empty."""
        with pytest.raises(MissingQueryParameterError) as excinfo:
            self.client.delete("")

        assert "host_id" in str(excinfo.value.message)
        assert excinfo.value.error_code == "E003"
        self.mock_scm.delete.assert_not_called()  # noqa

    def test_delete_http_error(self):
        """Test error handling for delete operation."""
        host_id = "non-existent-host"

        # Create a mock response to simulate an HTTP error
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.json.return_value = {
            "_errors": [
                {
                    "code": "E005",
                    "message": "Not Found",
                    "details": {"errorType": "Device not found"},
                }
            ],
            "_request_id": "test-request-id",
        }
        mock_http_error = HTTPError(response=mock_response)
        self.mock_scm.delete.side_effect = mock_http_error

        with pytest.raises(HTTPError) as excinfo:
            self.client.delete(host_id)

        assert excinfo.value.response.status_code == 404
        self.mock_scm.delete.assert_called_once_with(
            "/config/objects/v1/quarantined-devices",
            params={"host_id": host_id},
        )
