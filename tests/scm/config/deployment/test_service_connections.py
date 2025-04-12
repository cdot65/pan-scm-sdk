"""Unit tests for the ServiceConnection class."""

import uuid
from unittest.mock import MagicMock

import pytest

from scm.config.deployment import ServiceConnection
from scm.exceptions import InvalidObjectError, MissingQueryParameterError
from scm.models.deployment import (
    ServiceConnectionCreateModel,
    ServiceConnectionResponseModel,
    ServiceConnectionUpdateModel,
)


@pytest.fixture
def sample_service_connection_dict():
    """Return a sample service connection dictionary."""
    return {
        "id": str(uuid.uuid4()),
        "name": "test-connection",
        "folder": "Service Connections",
        "ipsec_tunnel": "test-tunnel",
        "region": "us-east-1",
        "onboarding_type": "classic",
        "subnets": ["10.0.0.0/24", "192.168.1.0/24"],
        "bgp_peer": {
            "local_ip_address": "192.168.1.1",
            "peer_ip_address": "192.168.1.2",
        },
        "protocol": {
            "bgp": {
                "enable": True,
                "peer_as": "65000",
            }
        },
        "source_nat": True,
    }


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
        assert "Invalid max_limit type" in str(excinfo.value)

    def test_init_with_negative_max_limit(self):
        """Test initialization with negative max_limit."""
        with pytest.raises(InvalidObjectError) as excinfo:
            ServiceConnection(self.mock_scm, max_limit=-1)
        assert "Invalid max_limit value" in str(excinfo.value)

    def test_init_with_excessive_max_limit(self):
        """Test initialization with excessive max_limit."""
        with pytest.raises(InvalidObjectError) as excinfo:
            service_connection = ServiceConnection(self.mock_scm)
            service_connection.max_limit = 2000
        assert "max_limit exceeds maximum allowed value" in str(excinfo.value)

    def test_max_limit_property_setter(self):
        """Test the max_limit property setter."""
        # Create service connection with default max_limit
        service_connection = ServiceConnection(self.mock_scm)
        assert service_connection.max_limit == service_connection.DEFAULT_MAX_LIMIT

        # Change max_limit value
        service_connection.max_limit = 500
        assert service_connection.max_limit == 500

        # Try invalid values
        with pytest.raises(InvalidObjectError) as excinfo:
            service_connection.max_limit = "invalid"
        assert "Invalid max_limit type" in str(excinfo.value)

        with pytest.raises(InvalidObjectError) as excinfo:
            service_connection.max_limit = -10
        assert "Invalid max_limit value" in str(excinfo.value)

        with pytest.raises(InvalidObjectError) as excinfo:
            service_connection.max_limit = 1500
        assert "max_limit exceeds maximum allowed value" in str(excinfo.value)

        # Confirm original value is unchanged after failed attempts
        assert service_connection.max_limit == 500

    def test_create(self, sample_service_connection_dict):
        """Test create method."""
        self.mock_scm.post.return_value = sample_service_connection_dict

        # Create a copy without the ID for create operation
        create_data = sample_service_connection_dict.copy()
        create_data.pop("id")

        result = self.client.create(create_data)

        # Check that correct API call was made
        self.mock_scm.post.assert_called_once()
        call_args = self.mock_scm.post.call_args
        assert call_args[0][0] == self.client.ENDPOINT

        # Check payload validation
        payload = call_args[1]["json"]
        # Should be deserialized from a ServiceConnectionCreateModel
        ServiceConnectionCreateModel(**payload)

        # Check result
        assert isinstance(result, ServiceConnectionResponseModel)
        assert result.name == sample_service_connection_dict["name"]
        assert result.folder == sample_service_connection_dict["folder"]

    def test_get(self, sample_service_connection_dict):
        """Test get method."""
        self.mock_scm.get.return_value = sample_service_connection_dict
        object_id = sample_service_connection_dict["id"]

        result = self.client.get(object_id)

        # Check that correct API call was made
        expected_endpoint = f"{self.client.ENDPOINT}/{object_id}"
        self.mock_scm.get.assert_called_once_with(expected_endpoint)

        # Check result
        assert isinstance(result, ServiceConnectionResponseModel)
        assert result.id == uuid.UUID(object_id)
        assert result.name == sample_service_connection_dict["name"]

    def test_update(self, sample_service_connection_dict):
        """Test update method."""
        self.mock_scm.put.return_value = sample_service_connection_dict
        object_id = sample_service_connection_dict["id"]

        # Create update model
        update_model = ServiceConnectionUpdateModel(**sample_service_connection_dict)

        result = self.client.update(update_model)

        # Check that correct API call was made
        expected_endpoint = f"{self.client.ENDPOINT}/{object_id}"
        self.mock_scm.put.assert_called_once()
        call_args = self.mock_scm.put.call_args
        assert call_args[0][0] == expected_endpoint

        # ID should not be in the payload since it's in the URL
        assert "id" not in call_args[1]["json"]

        # Check result
        assert isinstance(result, ServiceConnectionResponseModel)
        assert result.id == uuid.UUID(object_id)
        assert result.name == sample_service_connection_dict["name"]

    def test_delete(self, sample_service_connection_dict):
        """Test delete method."""
        object_id = sample_service_connection_dict["id"]

        self.client.delete(object_id)

        # Check that correct API call was made
        expected_endpoint = f"{self.client.ENDPOINT}/{object_id}"
        self.mock_scm.delete.assert_called_once_with(expected_endpoint)

    def test_list(self, sample_service_connection_dict):
        """Test list method."""
        self.mock_scm.get.return_value = {
            "data": [sample_service_connection_dict],
            "limit": 20,
            "offset": 0,
            "total": 1,
        }

        result = self.client.list()

        # Check that correct API call was made
        self.mock_scm.get.assert_called_once()
        call_args = self.mock_scm.get.call_args
        assert call_args[0][0] == self.client.ENDPOINT
        assert "folder" in call_args[1]["params"]
        assert call_args[1]["params"]["folder"] == "Service Connections"

        # Check result
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], ServiceConnectionResponseModel)
        assert result[0].name == sample_service_connection_dict["name"]

    def test_list_response_errors(self):
        """Test list method error handling for invalid responses."""
        # Test non-dictionary response
        self.mock_scm.get.return_value = ["not", "a", "dictionary"]
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.list()
        assert "Response is not a dictionary" in str(excinfo.value)

        # Test missing data field
        self.mock_scm.get.return_value = {"no_data": "field"}
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.list()
        assert '"data" field missing in the response' in str(excinfo.value)

        # Test data field not a list
        self.mock_scm.get.return_value = {"data": "not a list"}
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.list()
        assert '"data" field must be a list' in str(excinfo.value)

    def test_list_pagination(self, sample_service_connection_dict):
        """Test list method pagination."""
        # Create multiple pages of data
        conn1 = sample_service_connection_dict.copy()
        conn1["id"] = str(uuid.uuid4())
        conn1["name"] = "connection1"

        conn2 = sample_service_connection_dict.copy()
        conn2["id"] = str(uuid.uuid4())
        conn2["name"] = "connection2"

        # Mock responses for pagination
        self.mock_scm.get.side_effect = [
            # First page
            {"data": [conn1], "limit": 1, "offset": 0, "total": 2},
            # Second page
            {"data": [conn2], "limit": 1, "offset": 1, "total": 2},
            # Empty page (to end pagination)
            {"data": [], "limit": 1, "offset": 2, "total": 2},
        ]

        # Set a small limit to force pagination
        self.client.max_limit = 1
        result = self.client.list()

        # Should have made 3 calls (2 pages + 1 empty page to end pagination)
        assert self.mock_scm.get.call_count == 3

        # We should get both connections in the result
        assert len(result) == 2
        conn_names = [conn.name for conn in result]
        assert "connection1" in conn_names
        assert "connection2" in conn_names

    def test_list_with_name_filter(self, sample_service_connection_dict):
        """Test list method with name filter."""
        self.mock_scm.get.return_value = {
            "data": [sample_service_connection_dict],
            "limit": 20,
            "offset": 0,
            "total": 1,
        }

        result = self.client.list(name="test-connection")

        # Check that correct API call was made
        self.mock_scm.get.assert_called_once()
        call_args = self.mock_scm.get.call_args
        assert call_args[0][0] == self.client.ENDPOINT
        assert call_args[1]["params"]["name"] == "test-connection"

        # Check result
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].name == "test-connection"

    def test_list_with_empty_name_parameter(self):
        """Test list method with empty name parameter."""
        # Set up response for the mock
        self.mock_scm.get.return_value = {"data": []}

        # Empty name should not raise an error, as it's handled as falsy
        # and the name filter won't be applied
        result = self.client.list(name="")
        assert isinstance(result, list)
        assert len(result) == 0

        # Check that name parameter wasn't included in API call
        call_args = self.mock_scm.get.call_args
        assert "name" not in call_args[1]["params"]

    def test_list_with_invalid_name_filter_types(self):
        """Test list method with invalid name filter types."""
        # Set up a proper response for the mock to prevent additional errors
        self.mock_scm.get.return_value = {"data": []}

        # Test with whitespace only - should raise error
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.list(name="   ")
        assert excinfo.value.message == "Name filter must be a non-empty string"

        # Test with name that's too long (over 255 chars)
        long_name = "a" * 256
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.list(name=long_name)
        assert excinfo.value.message == "Name filter exceeds maximum length of 255 characters"

        # Test with non-string value
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.list(name=123)
        assert excinfo.value.message == "Name filter must be a non-empty string"

        # Test with invalid character in name
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.list(name="invalid@name")
        assert (
            excinfo.value.message
            == "Invalid name format. Name must contain only alphanumeric characters, underscores, and hyphens"
        )

    def test_list_folder_override(self, sample_service_connection_dict):
        """Test list method folder override."""
        self.mock_scm.get.return_value = {
            "data": [sample_service_connection_dict],
            "limit": 20,
            "offset": 0,
            "total": 1,
        }

        # Attempt to use a different folder (should be ignored/overridden)
        result = self.client.list(folder="Other Folder")

        # Check that the API call was made with the correct folder
        call_args = self.mock_scm.get.call_args
        assert call_args[1]["params"]["folder"] == "Service Connections"

        # Check result
        assert isinstance(result, list)
        assert len(result) == 1

    def test_fetch(self, sample_service_connection_dict):
        """Test fetch method with direct response."""
        self.mock_scm.get.return_value = sample_service_connection_dict

        result = self.client.fetch(name="test-connection")

        # Check that correct API call was made
        self.mock_scm.get.assert_called_once()
        call_args = self.mock_scm.get.call_args
        assert call_args[0][0] == self.client.ENDPOINT
        assert call_args[1]["params"]["name"] == "test-connection"
        assert call_args[1]["params"]["folder"] == "Service Connections"

        # Check result
        assert isinstance(result, ServiceConnectionResponseModel)
        assert result.name == sample_service_connection_dict["name"]

    def test_fetch_with_data_list(self, sample_service_connection_dict):
        """Test fetch method with data list response."""
        # Create a list response with one matching item
        list_response = {
            "data": [
                sample_service_connection_dict,  # Match
                {
                    "id": str(uuid.uuid4()),
                    "name": "other-connection",
                    "folder": "Service Connections",
                    "ipsec_tunnel": "test-tunnel",
                    "region": "us-east-1",
                },
            ]
        }
        self.mock_scm.get.return_value = list_response

        result = self.client.fetch(name="test-connection")

        # Check result is the matching connection
        assert isinstance(result, ServiceConnectionResponseModel)
        assert result.name == "test-connection"

    def test_fetch_with_empty_name(self):
        """Test fetch method with empty name parameter."""
        with pytest.raises(MissingQueryParameterError) as excinfo:
            self.client.fetch(name="")

        assert '"name" is not allowed to be empty' in str(excinfo.value)

    def test_fetch_with_no_results(self):
        """Test fetch method with no matching results."""
        # Empty data list
        self.mock_scm.get.return_value = {"data": []}

        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.fetch(name="non-existent")

        assert "Service connection not found" in str(excinfo.value)

    def test_fetch_with_non_dict_response(self):
        """Test fetch method with non-dictionary response."""
        # Mock a non-dictionary response to hit line 294
        self.mock_scm.get.return_value = ["not", "a", "dictionary"]

        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.fetch(name="test-connection")

        assert "Response is not a dictionary" in str(excinfo.value)

    def test_fetch_with_no_exact_match(self, sample_service_connection_dict):
        """Test fetch method with no exact match in results."""
        # List with no exact match
        modified_dict = sample_service_connection_dict.copy()
        modified_dict["name"] = "similar-connection"

        self.mock_scm.get.return_value = {"data": [modified_dict]}

        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.fetch(name="test-connection")

        assert "Service connection not found" in str(excinfo.value)

    def test_fetch_invalid_response(self):
        """Test fetch method with invalid response format."""
        # Response with neither id nor data
        self.mock_scm.get.return_value = {"error": "some error"}

        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.fetch(name="test-connection")

        assert "Response format not recognized" in str(excinfo.value)

    def test_fetch_with_no_exact_name_match(self):
        """Test fetch method with data list that has no exact match."""
        # Data list with similar but not identical name objects
        response_data = {
            "data": [
                {
                    "id": str(uuid.uuid4()),
                    "name": "test-connection-1",
                    "folder": "Service Connections",
                    "ipsec_tunnel": "test-tunnel",
                    "region": "us-east-1",
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "test-connection-2",
                    "folder": "Service Connections",
                    "ipsec_tunnel": "test-tunnel",
                    "region": "us-east-1",
                },
            ]
        }

        self.mock_scm.get.return_value = response_data

        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.fetch(name="test-connection")

        assert "Service connection not found" in str(excinfo.value)
