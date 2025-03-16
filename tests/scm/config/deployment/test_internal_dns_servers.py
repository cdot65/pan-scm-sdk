"""Tests for the InternalDnsServers service class."""

import uuid
import pytest
from unittest.mock import MagicMock, patch

from scm.client import Scm
from scm.config.deployment.internal_dns_servers import InternalDnsServers
from scm.models.deployment.internal_dns_servers import (
    InternalDnsServersCreateModel,
    InternalDnsServersUpdateModel,
    InternalDnsServersResponseModel,
)
from scm.exceptions import (
    InvalidObjectError,
    MissingQueryParameterError,
)


@pytest.fixture
def api_client():
    """Create a mock API client."""
    mock_client = MagicMock(spec=Scm)
    # Add any necessary attributes the InternalDnsServers class expects
    mock_client.api_base_url = "https://api.strata.paloaltonetworks.com"
    return mock_client


@pytest.fixture
def dns_servers(api_client):
    """Create an InternalDnsServers instance with a mock client."""
    return InternalDnsServers(api_client)


@pytest.fixture
def sample_dns_server_id():
    """Generate a sample DNS server ID."""
    return str(uuid.uuid4())


@pytest.fixture
def sample_dns_server_response(sample_dns_server_id):
    """Create a sample DNS server response."""
    return {
        "id": sample_dns_server_id,
        "name": "test-dns-server",
        "domain_name": ["example.com", "test.com"],
        "primary": "192.168.1.1",
        "secondary": "8.8.8.8",
    }


class TestInternalDnsServers:
    """Tests for the InternalDnsServers service class."""

    def test_init(self, dns_servers):
        """Test initialization of InternalDnsServers."""
        assert dns_servers.ENDPOINT == "/config/deployment/v1/internal-dns-servers"
        assert dns_servers.DEFAULT_MAX_LIMIT == 2500
        assert dns_servers.ABSOLUTE_MAX_LIMIT == 5000
        assert dns_servers.max_limit == 2500

    def test_max_limit_property(self, dns_servers):
        """Test max_limit property."""
        dns_servers.max_limit = 1000
        assert dns_servers.max_limit == 1000

    def test_validate_max_limit_default(self, dns_servers):
        """Test _validate_max_limit with default."""
        assert dns_servers._validate_max_limit(None) == 2500

    def test_validate_max_limit_valid(self, dns_servers):
        """Test _validate_max_limit with valid value."""
        assert dns_servers._validate_max_limit(1000) == 1000

    def test_validate_max_limit_invalid_type(self, dns_servers):
        """Test _validate_max_limit with invalid type."""
        with pytest.raises(InvalidObjectError) as exc_info:
            dns_servers._validate_max_limit("invalid")
        error = exc_info.value
        # Check the actual attributes instead of string representation
        assert error.message == "max_limit must be an integer"
        assert error.details == {"error": "Invalid max_limit type"}

    def test_validate_max_limit_too_low(self, dns_servers):
        """Test _validate_max_limit with too low value."""
        with pytest.raises(InvalidObjectError) as exc_info:
            dns_servers._validate_max_limit(0)
        error = exc_info.value
        # Check the actual attributes instead of string representation
        assert error.message == "max_limit must be greater than 0"
        assert error.details == {"error": "Invalid max_limit value"}

    def test_validate_max_limit_too_high(self, dns_servers):
        """Test _validate_max_limit with too high value."""
        with pytest.raises(InvalidObjectError) as exc_info:
            dns_servers._validate_max_limit(6000)
        error = exc_info.value
        # Check the actual attributes instead of string representation
        assert error.message == f"max_limit cannot exceed {dns_servers.ABSOLUTE_MAX_LIMIT}"
        assert error.details == {"error": "max_limit exceeds maximum allowed value"}

    def test_create(self, dns_servers, api_client, sample_dns_server_response):
        """Test creating a DNS server."""
        api_client.post.return_value = sample_dns_server_response
        data = {
            "name": "test-dns-server",
            "domain_name": ["example.com", "test.com"],
            "primary": "192.168.1.1",
            "secondary": "8.8.8.8"
        }

        result = dns_servers.create(data)

        api_client.post.assert_called_once()
        assert isinstance(result, InternalDnsServersResponseModel)
        assert result.name == "test-dns-server"
        assert result.domain_name == ["example.com", "test.com"]

    def test_get(self, dns_servers, api_client, sample_dns_server_id, sample_dns_server_response):
        """Test getting a DNS server by ID."""
        api_client.get.return_value = sample_dns_server_response

        result = dns_servers.get(sample_dns_server_id)

        api_client.get.assert_called_once_with(f"{dns_servers.ENDPOINT}/{sample_dns_server_id}")
        assert isinstance(result, InternalDnsServersResponseModel)
        assert result.id == uuid.UUID(sample_dns_server_id)
        assert result.name == "test-dns-server"

    def test_update(self, dns_servers, api_client, sample_dns_server_id, sample_dns_server_response):
        """Test updating a DNS server."""
        api_client.put.return_value = sample_dns_server_response
        dns_server = InternalDnsServersUpdateModel(
            id=sample_dns_server_id,
            name="updated-dns-server",
            domain_name=["updated.com"]
        )

        result = dns_servers.update(dns_server)

        api_client.put.assert_called_once()
        assert isinstance(result, InternalDnsServersResponseModel)
        assert result.id == uuid.UUID(sample_dns_server_id)

    def test_list(self, dns_servers, api_client):
        """Test listing DNS servers."""
        mock_response = {
            "data": [
                {
                    "id": str(uuid.uuid4()),
                    "name": "server1",
                    "domain_name": ["example1.com"],
                    "primary": "192.168.1.1",
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "server2",
                    "domain_name": ["example2.com"],
                    "primary": "192.168.1.2",
                }
            ],
            "limit": 2500,
            "offset": 0,
            "total": 2
        }
        api_client.get.return_value = mock_response

        result = dns_servers.list(name="test")

        api_client.get.assert_called_once()
        assert len(result) == 2
        assert all(isinstance(item, InternalDnsServersResponseModel) for item in result)

    def test_list_pagination(self, dns_servers, api_client):
        """Test listing DNS servers with pagination."""
        # First page
        first_response = {
            "data": [{"id": str(uuid.uuid4()), "name": "server1", "domain_name": ["example1.com"], "primary": "192.168.1.1"}],
            "limit": 1,
            "offset": 0,
            "total": 2
        }
        # Second page - make sure offset is correct
        second_response = {
            "data": [{"id": str(uuid.uuid4()), "name": "server2", "domain_name": ["example2.com"], "primary": "192.168.1.2"}],
            "limit": 1,
            "offset": 1,
            "total": 2
        }
        # Empty third page to signal the end
        third_response = {
            "data": [],
            "limit": 1,
            "offset": 2,
            "total": 2
        }
        
        api_client.get.side_effect = [first_response, second_response, third_response]
        dns_servers._max_limit = 1  # Set small limit to force pagination

        result = dns_servers.list()

        assert api_client.get.call_count == 3
        assert len(result) == 2

    def test_list_invalid_response_not_dict(self, dns_servers, api_client):
        """Test list with invalid response (not a dict)."""
        api_client.get.return_value = "invalid"

        with pytest.raises(InvalidObjectError) as exc_info:
            dns_servers.list()
        error = exc_info.value
        # Check the actual attributes instead of string representation
        assert error.message == "Invalid response format: expected dictionary"
        assert error.details == {"error": "Response is not a dictionary"}

    def test_list_invalid_response_no_data(self, dns_servers, api_client):
        """Test list with invalid response (no data field)."""
        api_client.get.return_value = {}

        with pytest.raises(InvalidObjectError) as exc_info:
            dns_servers.list()
        error = exc_info.value
        # Check the actual attributes instead of string representation
        assert error.message == "Invalid response format: missing 'data' field"
        assert error.details == {"field": "data", "error": '"data" field missing in the response'}

    def test_list_invalid_response_data_not_list(self, dns_servers, api_client):
        """Test list with invalid response (data not a list)."""
        api_client.get.return_value = {"data": "invalid"}

        with pytest.raises(InvalidObjectError) as exc_info:
            dns_servers.list()
        error = exc_info.value
        # Check the actual attributes instead of string representation
        assert error.message == "Invalid response format: 'data' field must be a list"
        assert error.details == {"field": "data", "error": '"data" field must be a list'}

    def test_fetch(self, dns_servers, api_client, sample_dns_server_response):
        """Test fetching a DNS server by name."""
        api_client.get.return_value = sample_dns_server_response

        result = dns_servers.fetch("test-dns-server")

        api_client.get.assert_called_once()
        assert isinstance(result, InternalDnsServersResponseModel)
        assert result.name == "test-dns-server"

    def test_fetch_missing_name(self, dns_servers):
        """Test fetch with missing name parameter."""
        with pytest.raises(MissingQueryParameterError) as exc_info:
            dns_servers.fetch("")
        error = exc_info.value
        # Check the actual attributes instead of string representation
        assert error.message == "Field 'name' cannot be empty"
        assert error.details == {"field": "name", "error": '"name" is not allowed to be empty'}
        
    def test_fetch_response_not_dict(self, dns_servers, api_client):
        """Test fetch with response that is not a dictionary."""
        # Set the API client to return a non-dictionary value
        api_client.get.return_value = "not a dictionary"
        
        with pytest.raises(InvalidObjectError) as exc_info:
            dns_servers.fetch("test-dns-server")
        error = exc_info.value
        # Check the actual attributes instead of string representation
        assert error.message == "Invalid response format: expected dictionary"
        assert error.details == {"error": "Response is not a dictionary"}

    def test_fetch_data_array_response(self, dns_servers, api_client, sample_dns_server_response):
        """Test fetch with data array response format."""
        sample_response_with_data = {"data": [sample_dns_server_response]}
        api_client.get.return_value = sample_response_with_data

        result = dns_servers.fetch("test-dns-server")

        assert isinstance(result, InternalDnsServersResponseModel)
        assert result.name == "test-dns-server"

    def test_fetch_empty_data_array(self, dns_servers, api_client):
        """Test fetch with empty data array."""
        api_client.get.return_value = {"data": []}

        with pytest.raises(InvalidObjectError) as exc_info:
            dns_servers.fetch("test-dns-server")
        error = exc_info.value
        # Check the actual attributes instead of string representation
        assert error.message == "Internal DNS server 'test-dns-server' not found"
        assert error.details == {"error": "No matching internal DNS server found"}

    def test_fetch_invalid_data_item(self, dns_servers, api_client):
        """Test fetch with invalid data item (no id)."""
        api_client.get.return_value = {"data": [{"name": "test"}]}

        with pytest.raises(InvalidObjectError) as exc_info:
            dns_servers.fetch("test-dns-server")
        error = exc_info.value
        # Check the actual attributes instead of string representation
        assert error.message == "Invalid response format: missing 'id' field in data array"
        assert error.details == {"error": "Response data item missing 'id' field"}

    def test_fetch_multiple_items(self, dns_servers, api_client, sample_dns_server_response):
        """Test fetch with multiple items returned."""
        second_response = sample_dns_server_response.copy()
        second_response["id"] = str(uuid.uuid4())
        sample_response_with_data = {"data": [sample_dns_server_response, second_response]}
        api_client.get.return_value = sample_response_with_data

        with patch.object(dns_servers, 'logger') as mock_logger:
            result = dns_servers.fetch("test-dns-server")
            mock_logger.warning.assert_called_once()

        assert isinstance(result, InternalDnsServersResponseModel)
        assert result.id == uuid.UUID(sample_dns_server_response["id"])

    def test_fetch_invalid_response_format(self, dns_servers, api_client):
        """Test fetch with invalid response format."""
        api_client.get.return_value = {"invalid": "response"}

        with pytest.raises(InvalidObjectError) as exc_info:
            dns_servers.fetch("test-dns-server")
        error = exc_info.value
        # Check the actual attributes instead of string representation
        assert error.message == "Invalid response format: expected either 'id' or 'data' field"
        assert error.details == {"error": "Response has invalid structure"}

    def test_delete(self, dns_servers, api_client, sample_dns_server_id):
        """Test deleting a DNS server."""
        dns_servers.delete(sample_dns_server_id)

        api_client.delete.assert_called_once_with(f"{dns_servers.ENDPOINT}/{sample_dns_server_id}")
