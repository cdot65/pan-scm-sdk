# tests/scm/config/objects/test_quarantined_devices.py

# Standard library imports
from unittest.mock import MagicMock

import pytest
from requests.exceptions import HTTPError

# Local SDK imports
from scm.config.objects import QuarantinedDevices
from scm.exceptions import InvalidObjectError, MissingQueryParameterError
from scm.models.objects import QuarantinedDevicesResponseModel
from tests.utils import raise_mock_http_error


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
        mock_response = [
            {
                "host_id": "host-1",
                "serial_number": "serial-1",
            },
            {
                "host_id": "host-2",
                "serial_number": "serial-2",
            },
        ]
        self.mock_scm.get.return_value = mock_response  # noqa

        result = self.client.list()

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/objects/v1/quarantined-devices",
            params={},
        )
        assert len(result) == 2
        assert isinstance(result[0], QuarantinedDevicesResponseModel)
        assert result[0].host_id == "host-1"
        assert result[0].serial_number == "serial-1"
        assert result[1].host_id == "host-2"
        assert result[1].serial_number == "serial-2"

    def test_list_with_host_id_filter(self):
        """Test listing quarantined devices filtered by host_id."""
        mock_response = [
            {
                "host_id": "host-1",
                "serial_number": "serial-1",
            },
        ]
        self.mock_scm.get.return_value = mock_response  # noqa

        result = self.client.list(host_id="host-1")

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/objects/v1/quarantined-devices",
            params={"host_id": "host-1"},
        )
        assert len(result) == 1
        assert isinstance(result[0], QuarantinedDevicesResponseModel)
        assert result[0].host_id == "host-1"
        assert result[0].serial_number == "serial-1"

    def test_list_with_serial_number_filter(self):
        """Test listing quarantined devices filtered by serial_number."""
        mock_response = [
            {
                "host_id": "host-2",
                "serial_number": "serial-2",
            },
        ]
        self.mock_scm.get.return_value = mock_response  # noqa

        result = self.client.list(serial_number="serial-2")

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/objects/v1/quarantined-devices",
            params={"serial_number": "serial-2"},
        )
        assert len(result) == 1
        assert isinstance(result[0], QuarantinedDevicesResponseModel)
        assert result[0].host_id == "host-2"
        assert result[0].serial_number == "serial-2"

    def test_list_with_both_filters(self):
        """Test listing quarantined devices with both filters."""
        mock_response = [
            {
                "host_id": "host-1",
                "serial_number": "serial-1",
            },
        ]
        self.mock_scm.get.return_value = mock_response  # noqa

        result = self.client.list(host_id="host-1", serial_number="serial-1")

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/objects/v1/quarantined-devices",
            params={"host_id": "host-1", "serial_number": "serial-1"},
        )
        assert len(result) == 1
        assert isinstance(result[0], QuarantinedDevicesResponseModel)
        assert result[0].host_id == "host-1"
        assert result[0].serial_number == "serial-1"

    def test_list_empty_response(self):
        """Test listing quarantined devices with empty response."""
        mock_response = []
        self.mock_scm.get.return_value = mock_response  # noqa

        result = self.client.list()

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/objects/v1/quarantined-devices",
            params={},
        )
        assert len(result) == 0

    def test_list_invalid_response_format(self):
        """Test that InvalidObjectError is raised when response is not a list."""
        self.mock_scm.get.return_value = {"invalid": "format"}  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list()

        error_msg = str(exc_info.value)
        assert "Response is not a list" in error_msg
        assert "E003" in error_msg
        assert "500" in error_msg

    def test_list_http_error(self):
        """Test error handling for list operation."""
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=500,
            error_code="E003",
            message="Internal server error",
            error_type="Server Error",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.list()

        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "Internal server error"
        assert error_response["_errors"][0]["details"]["errorType"] == "Server Error"


class TestQuarantinedDevicesCreate(TestQuarantinedDevicesBase):
    """Tests for creating Quarantined Devices."""

    def test_create_success(self):
        """Test successful creation of a quarantined device."""
        test_data = {
            "host_id": "test-host-id",
            "serial_number": "test-serial-number",
        }
        mock_response = {
            "host_id": "test-host-id",
            "serial_number": "test-serial-number",
        }
        self.mock_scm.post.return_value = mock_response  # noqa

        result = self.client.create(test_data)

        self.mock_scm.post.assert_called_once_with(  # noqa
            "/config/objects/v1/quarantined-devices",
            json=test_data,
        )
        assert isinstance(result, QuarantinedDevicesResponseModel)
        assert result.host_id == "test-host-id"
        assert result.serial_number == "test-serial-number"

    def test_create_minimal_data(self):
        """Test creation with minimal required data."""
        test_data = {
            "host_id": "test-host-id",
        }
        mock_response = {
            "host_id": "test-host-id",
        }
        self.mock_scm.post.return_value = mock_response  # noqa

        result = self.client.create(test_data)

        self.mock_scm.post.assert_called_once_with(  # noqa
            "/config/objects/v1/quarantined-devices",
            json=test_data,
        )
        assert isinstance(result, QuarantinedDevicesResponseModel)
        assert result.host_id == "test-host-id"
        assert result.serial_number is None

    def test_create_missing_required_field(self):
        """Test that validation error is raised if host_id is missing."""
        test_data = {"serial_number": "test-serial-number"}

        with pytest.raises(ValueError) as exc_info:
            self.client.create(test_data)

        assert "host_id" in str(exc_info.value)
        self.mock_scm.post.assert_not_called()  # noqa

    def test_create_http_error(self):
        """Test error handling for create operation."""
        test_data = {
            "host_id": "test-host-id",
            "serial_number": "test-serial-number",
        }
        self.mock_scm.post.side_effect = raise_mock_http_error(  # noqa
            status_code=400,
            error_code="E003",
            message="Invalid request",
            error_type="Invalid Object",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.create(test_data)

        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "Invalid request"
        assert error_response["_errors"][0]["details"]["errorType"] == "Invalid Object"


class TestQuarantinedDevicesDelete(TestQuarantinedDevicesBase):
    """Tests for deleting Quarantined Devices."""

    def test_delete_success(self):
        """Test successful deletion of a quarantined device."""
        self.mock_scm.delete.return_value = None  # noqa

        self.client.delete("test-host-id")

        self.mock_scm.delete.assert_called_once_with(  # noqa
            "/config/objects/v1/quarantined-devices",
            params={"host_id": "test-host-id"},
        )

    def test_delete_empty_host_id(self):
        """Test that MissingQueryParameterError is raised if host_id is empty."""
        with pytest.raises(MissingQueryParameterError) as exc_info:
            self.client.delete("")

        error_msg = str(exc_info.value)
        assert "'host_id' is not allowed to be empty" in error_msg
        assert "E003" in error_msg
        assert "400" in error_msg
        self.mock_scm.delete.assert_not_called()  # noqa

    def test_delete_http_error(self):
        """Test error handling for delete operation."""
        self.mock_scm.delete.side_effect = raise_mock_http_error(  # noqa
            status_code=404,
            error_code="E005",
            message="Object not found",
            error_type="Object Not Present",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.delete("test-host-id")

        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "Object not found"
        assert error_response["_errors"][0]["details"]["errorType"] == "Object Not Present"
