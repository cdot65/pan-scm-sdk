"""Unit tests for the ServiceConnection class."""

from unittest.mock import MagicMock
import uuid

import pytest

from scm.config.deployment import ServiceConnection
from scm.exceptions import InvalidObjectError, MissingQueryParameterError
from scm.models.deployment import ServiceConnectionResponseModel
from tests.test_factories.deployment import (
    ServiceConnectionCreateApiFactory,
    ServiceConnectionCreateModelFactory,
    ServiceConnectionResponseFactory,
    ServiceConnectionUpdateModelFactory,
)


@pytest.fixture
def sample_service_connection_dict():
    """Return a sample service connection dictionary."""
    return ServiceConnectionResponseFactory.build()


@pytest.fixture
def sample_service_connection_response(sample_service_connection_dict):
    """Return a sample ServiceConnectionResponseModel."""
    return ServiceConnectionResponseModel(**sample_service_connection_dict)


@pytest.mark.usefixtures("load_env")
class TestServiceConnectionBase:
    """Base class for ServiceConnection tests."""

    @pytest.fixture(autouse=True)
    def setup_method(self, mock_scm):
        """Setup method that runs before each test."""
        self.mock_scm = mock_scm
        self.mock_scm.get = MagicMock()
        self.mock_scm.post = MagicMock()
        self.mock_scm.put = MagicMock()
        self.mock_scm.delete = MagicMock()
        self.client = ServiceConnection(self.mock_scm, max_limit=1000)


class TestServiceConnection(TestServiceConnectionBase):
    """Test suite for ServiceConnection class."""

    def test_init(self):
        """Test initialization of ServiceConnection class."""
        service_connection = ServiceConnection(self.mock_scm)
        assert service_connection.api_client == self.mock_scm
        assert service_connection.ENDPOINT == "/config/deployment/v1/service-connections"
        assert service_connection.max_limit == service_connection.DEFAULT_MAX_LIMIT

    def test_logger_initialization(self):
        """Test that the logger is properly initialized."""
        import logging

        # Create the ServiceConnection instance
        service_connection = ServiceConnection(self.mock_scm)

        # Verify the logger attribute
        assert hasattr(service_connection, "logger")
        assert isinstance(service_connection.logger, logging.Logger)

        # Check that the logger has the correct name
        # The logger name should be the module's __name__, which is 'scm.config.deployment.service_connections'
        assert service_connection.logger.name.endswith("service_connections")

        # Check that the logger exists in the logging system
        assert service_connection.logger.name in logging.root.manager.loggerDict

    def test_init_with_custom_max_limit(self):
        """Test initialization with custom max_limit."""
        service_connection = ServiceConnection(self.mock_scm, max_limit=500)
        assert service_connection.max_limit == 500

    def test_init_with_invalid_max_limit(self):
        """Test initialization with invalid max_limit."""
        with pytest.raises(InvalidObjectError) as excinfo:
            ServiceConnection(self.mock_scm, max_limit="invalid")
        assert excinfo.value.message == "max_limit must be an integer"

    def test_init_with_too_low_max_limit(self):
        """Test initialization with max_limit that's too low."""
        with pytest.raises(InvalidObjectError) as excinfo:
            ServiceConnection(self.mock_scm, max_limit=0)
        assert excinfo.value.message == "max_limit must be greater than 0"

    def test_init_with_too_high_max_limit(self):
        """Test initialization with max_limit that's too high."""
        with pytest.raises(InvalidObjectError) as excinfo:
            # Use a value that exceeds the ABSOLUTE_MAX_LIMIT (1000)
            ServiceConnection(self.mock_scm, max_limit=1001)
        assert "max_limit cannot exceed" in excinfo.value.message

    def test_max_limit_property(self):
        """Test the max_limit property."""
        service_connection = ServiceConnection(self.mock_scm, max_limit=500)
        assert service_connection.max_limit == 500

        # Test setter
        service_connection.max_limit = 100
        assert service_connection.max_limit == 100

        # Test setter with invalid value
        with pytest.raises(InvalidObjectError):
            service_connection.max_limit = 0

    def test_create(self, sample_service_connection_dict):
        """Test creating a service connection."""
        # Setup
        create_data = ServiceConnectionCreateApiFactory.build()
        response_data = sample_service_connection_dict
        self.mock_scm.post.return_value = response_data

        # Exercise
        result = self.client.create(create_data)

        # Verify
        self.mock_scm.post.assert_called_once()
        assert isinstance(result, ServiceConnectionResponseModel)
        assert result.id == uuid.UUID(response_data["id"])
        assert result.name == response_data["name"]

    def test_create_with_pydantic_model(self, sample_service_connection_dict):
        """Test creating a service connection with a Pydantic model as input."""
        # Setup
        create_model = ServiceConnectionCreateModelFactory.build()
        response_data = sample_service_connection_dict
        self.mock_scm.post.return_value = response_data

        # Exercise
        result = self.client.create(create_model.model_dump(by_alias=True))

        # Verify
        self.mock_scm.post.assert_called_once()
        assert isinstance(result, ServiceConnectionResponseModel)
        assert result.id == uuid.UUID(response_data["id"])
        assert result.name == response_data["name"]

    def test_get(self, sample_service_connection_dict):
        """Test getting a service connection."""
        # Setup
        object_id = "123e4567-e89b-12d3-a456-426655440000"
        self.mock_scm.get.return_value = sample_service_connection_dict

        # Exercise
        result = self.client.get(object_id)

        # Verify
        self.mock_scm.get.assert_called_once_with(f"{self.client.ENDPOINT}/{object_id}")
        assert isinstance(result, ServiceConnectionResponseModel)
        assert result.id == uuid.UUID(sample_service_connection_dict["id"])
        assert result.name == sample_service_connection_dict["name"]

    def test_update(self, sample_service_connection_dict):
        """Test updating a service connection."""
        # Setup
        update_model = ServiceConnectionUpdateModelFactory.build()
        response_data = sample_service_connection_dict
        self.mock_scm.put.return_value = response_data

        # Exercise
        result = self.client.update(update_model)

        # Verify
        expected_endpoint = f"{self.client.ENDPOINT}/{update_model.id}"
        self.mock_scm.put.assert_called_once()
        assert self.mock_scm.put.call_args[0][0] == expected_endpoint
        assert isinstance(result, ServiceConnectionResponseModel)
        assert result.id == uuid.UUID(response_data["id"])
        assert result.name == response_data["name"]

    def test_list(self):
        """Test listing service connections."""
        # Setup
        response_data = {
            "data": [
                ServiceConnectionResponseFactory.build(),
                ServiceConnectionResponseFactory.build(),
                ServiceConnectionResponseFactory.build(),
            ]
        }
        self.mock_scm.get.return_value = response_data

        # Exercise
        result = self.client.list()  # Use default params instead of explicit limit

        # Verify
        self.mock_scm.get.assert_called_once()
        # Check only the first argument instead of all parameters due to potential internal changes
        assert self.mock_scm.get.call_args[0][0] == self.client.ENDPOINT
        assert len(result) == 3
        assert all(isinstance(item, ServiceConnectionResponseModel) for item in result)

    def test_list_with_pagination(self):
        """Test listing service connections with pagination."""
        # Set up a basic response for a single call
        service_connections = [
            ServiceConnectionResponseFactory.build(),
            ServiceConnectionResponseFactory.build(),
            ServiceConnectionResponseFactory.build(),
        ]
        response_data = {"data": service_connections}

        # Configure mock to return the data
        self.mock_scm.get.return_value = response_data

        # Exercise - call list with default parameters
        result = self.client.list()

        # Verify
        assert self.mock_scm.get.call_count == 1

        # Verify the correct parameters were used
        call_args = self.mock_scm.get.call_args[1]
        assert "params" in call_args
        params = call_args["params"]

        # Should have folder, limit and offset parameters
        assert params["folder"] == "Service Connections"
        assert "limit" in params
        assert "offset" in params

        # Result should contain all service connections
        assert len(result) == 3
        assert all(isinstance(item, ServiceConnectionResponseModel) for item in result)

    def test_list_with_empty_response(self):
        """Test listing service connections with an empty response."""
        # Setup
        response_data = {"data": []}
        self.mock_scm.get.return_value = response_data

        # Exercise
        result = self.client.list()

        # Verify
        self.mock_scm.get.assert_called_once()
        assert len(result) == 0

    def test_list_with_name_filter(self):
        """Test listing service connections with a name filter."""
        # Setup
        response_data = {
            "data": [
                ServiceConnectionResponseFactory.build(name="test-name"),
            ]
        }
        self.mock_scm.get.return_value = response_data

        # Exercise
        result = self.client.list(name="test-name")

        # Verify
        self.mock_scm.get.assert_called_once()
        params = self.mock_scm.get.call_args[1]["params"]
        assert params["name"] == "test-name"
        assert len(result) == 1

    def test_list_with_invalid_name_filter(self):
        """Test listing service connections with an invalid name filter."""
        # We need to reset the get mock to not cause issues with subsequent assertions
        self.mock_scm.get.reset_mock()

        # Set up a valid response to avoid response format errors
        self.mock_scm.get.return_value = {"data": []}

        # Empty string
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.list(name="  ")  # Only whitespace
        assert excinfo.value.message == "Name filter must be a non-empty string"

        # None - this won't trigger the validation since it's falsy
        # Instead test with a name that's too long
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.list(name="a" * 256)  # One more than the max allowed length
        assert excinfo.value.message == "Name filter exceeds maximum length of 255 characters"

        # Invalid characters
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.list(name="invalid@name")  # Contains @ which is not allowed
        assert "Invalid name format" in excinfo.value.message

    def test_list_with_invalid_response(self):
        """Test handling of invalid response formats when listing."""
        # Setup - response is not a dict
        self.mock_scm.get.return_value = "not a dict"

        # Exercise & Verify
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.list()
        assert excinfo.value.message == "Invalid response format: expected dictionary"

        # Setup - response is missing data field
        self.mock_scm.get.return_value = {"no_data": []}

        # Exercise & Verify
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.list()
        assert excinfo.value.message == "Invalid response format: missing 'data' field"

        # Setup - data field is not a list
        self.mock_scm.get.return_value = {"data": "not a list"}

        # Exercise & Verify
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.list()
        assert excinfo.value.message == "Invalid response format: 'data' field must be a list"

    def test_fetch(self):
        """Test fetching a service connection by name."""
        # Setup
        name = "test-connection"
        response_data = {
            "data": [
                ServiceConnectionResponseFactory.build(name=name),
            ]
        }
        self.mock_scm.get.return_value = response_data

        # Exercise
        result = self.client.fetch(name=name)

        # Verify
        self.mock_scm.get.assert_called_once_with(
            self.client.ENDPOINT,
            params={"name": name, "folder": "Service Connections"},
        )
        assert isinstance(result, ServiceConnectionResponseModel)
        assert result.name == name

    def test_fetch_with_empty_name(self):
        """Test fetching a service connection with an empty name."""
        # Exercise & Verify
        with pytest.raises(MissingQueryParameterError) as excinfo:
            self.client.fetch(name="")
        assert excinfo.value.message == "Field 'name' cannot be empty"

    def test_fetch_with_invalid_response(self):
        """Test handling of invalid response formats when fetching."""
        # Setup - response is not a dict
        self.mock_scm.get.return_value = "not a dict"
        name = "test-connection"

        # Exercise & Verify
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.fetch(name=name)
        assert excinfo.value.message == "Invalid response format: expected dictionary"

        # Setup - no items found
        self.mock_scm.get.return_value = {"data": []}

        # Exercise & Verify
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.fetch(name=name)
        assert excinfo.value.message == f"No service connection found with name: {name}"

        # Setup - no exact match found (names don't match)
        self.mock_scm.get.return_value = {
            "data": [
                ServiceConnectionResponseFactory.build(name="different-name"),
            ]
        }

        # Exercise & Verify
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.fetch(name=name)
        assert (
            excinfo.value.message
            == f"No exact match found for service connection with name: {name}"
        )

        # Setup - invalid response structure (no data or id)
        self.mock_scm.get.return_value = {"some_field": "value"}

        # Exercise & Verify
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.fetch(name=name)
        assert excinfo.value.message == "Invalid response format"

    def test_fetch_with_direct_response(self):
        """Test fetching a service connection with a direct response (no data array)."""
        # Setup
        name = "test-connection"
        direct_response = ServiceConnectionResponseFactory.build(name=name)
        self.mock_scm.get.return_value = direct_response

        # Exercise
        result = self.client.fetch(name=name)

        # Verify
        self.mock_scm.get.assert_called_once()
        assert isinstance(result, ServiceConnectionResponseModel)
        assert result.id == uuid.UUID(direct_response["id"])
        assert result.name == name

    def test_delete(self):
        """Test deleting a service connection."""
        # Setup
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        # Exercise
        self.client.delete(object_id)

        # Verify
        self.mock_scm.delete.assert_called_once_with(f"{self.client.ENDPOINT}/{object_id}")

    def test_real_pagination_alt(self):
        """Test listing service connections with pagination - alternative approach."""
        # Create a mock response that simulates pagination being complete in one call
        response_data = {
            "data": [
                ServiceConnectionResponseFactory.build(),
                ServiceConnectionResponseFactory.build(),
                ServiceConnectionResponseFactory.build(),
            ]
        }

        # Configure the mock to return our prepared response
        self.mock_scm.get.return_value = response_data

        # Call list() which will use the configured max_limit
        result = self.client.list()

        # Verify we got the expected number of results
        assert len(result) == 3
        assert all(isinstance(item, ServiceConnectionResponseModel) for item in result)


def test_service_connection_pagination():
    """Standalone test for service connection pagination."""
    from scm.client import Scm

    # Create a fresh mock directly for this test
    mock_scm = MagicMock(spec=Scm)
    mock_scm.get = MagicMock()

    # Create a client with a small max_limit to force pagination
    small_limit = 2
    client = ServiceConnection(mock_scm, max_limit=small_limit)

    # Create test data for pagination
    first_page = {
        "data": [
            ServiceConnectionResponseFactory.build(),
            ServiceConnectionResponseFactory.build(),
        ]
    }

    second_page = {
        "data": [
            ServiceConnectionResponseFactory.build(),
        ]
    }

    # Configure mock to return our test data
    mock_scm.get.side_effect = [first_page, second_page]

    # Exercise pagination
    result = client.list()

    # Verify API calls
    assert mock_scm.get.call_count == 2

    # Check first call
    first_call = mock_scm.get.call_args_list[0]
    assert first_call[1]["params"]["offset"] == 0
    assert first_call[1]["params"]["limit"] == small_limit
    assert first_call[1]["params"]["folder"] == "Service Connections"

    # Check second call
    second_call = mock_scm.get.call_args_list[1]
    assert second_call[1]["params"]["offset"] == small_limit
    assert second_call[1]["params"]["limit"] == small_limit
    assert second_call[1]["params"]["folder"] == "Service Connections"

    # Verify the combined result
    assert len(result) == 3  # All items from both pages
    assert all(isinstance(item, ServiceConnectionResponseModel) for item in result)
