"""Tests for the IKE Gateway service class."""

import json
import pytest
from unittest.mock import MagicMock, patch
from uuid import UUID

from scm.config.network import IKEGateway
from scm.exceptions import InvalidObjectError, MissingQueryParameterError
from scm.models.network import (
    IKEGatewayResponseModel,
    IKEGatewayUpdateModel,
)


# Test data
MOCK_IKE_GATEWAY = {
    "id": "123e4567-e89b-12d3-a456-426655440000",
    "name": "test-ike-gateway",
    "folder": "test-folder",
    "authentication": {
        "pre_shared_key": {
            "key": "secret-key"
        }
    },
    "peer_id": {
        "type": "ipaddr",
        "id": "10.0.0.1"
    },
    "protocol": {
        "version": "ikev2",
        "ikev2": {
            "ike_crypto_profile": "default",
            "dpd": {
                "enable": True
            }
        }
    },
    "peer_address": {
        "ip": "10.0.0.1"
    }
}


@pytest.mark.usefixtures("load_env")
class TestIKEGatewayBase:
    """Base class for IKEGateway tests."""

    @pytest.fixture(autouse=True)
    def setup_method(self, mock_scm):
        """Setup method that runs before each test."""
        self.mock_scm = mock_scm
        self.mock_scm.get = MagicMock()
        self.mock_scm.post = MagicMock()
        self.mock_scm.put = MagicMock()
        self.mock_scm.delete = MagicMock()
        self.client = IKEGateway(self.mock_scm, max_limit=5000)


class TestIKEGateway(TestIKEGatewayBase):
    """Test suite for IKEGateway class."""

    def test_init_default_limit(self):
        """Test initializing with default max limit."""
        service = IKEGateway(self.mock_scm)
        assert service.max_limit == 2500
        assert service.ENDPOINT == "/config/network/v1/ike-gateways"

    def test_init_custom_limit(self):
        """Test initializing with custom max limit."""
        service = IKEGateway(self.mock_scm, max_limit=1000)
        assert service.max_limit == 1000

    def test_set_max_limit(self):
        """Test setting the max_limit via property."""
        self.client.max_limit = 3000
        assert self.client.max_limit == 3000

    def test_max_limit_validation_invalid_type(self):
        """Test validation of max_limit with invalid type."""
        with pytest.raises(InvalidObjectError) as exc_info:
            IKEGateway(self.mock_scm, max_limit="invalid")
        
        # Check the error details instead of the exact message
        assert "Invalid max_limit type" in str(exc_info.value)

    def test_max_limit_validation_less_than_one(self):
        """Test validation of max_limit with value less than 1."""
        with pytest.raises(InvalidObjectError) as exc_info:
            IKEGateway(self.mock_scm, max_limit=0)
        
        # Check the error details instead of the exact message
        assert "Invalid max_limit value" in str(exc_info.value)

    def test_max_limit_validation_exceeds_max(self):
        """Test validation of max_limit with value that exceeds max."""
        with pytest.raises(InvalidObjectError) as exc_info:
            IKEGateway(self.mock_scm, max_limit=6000)
        
        # Check the error details instead of the exact message
        assert "max_limit exceeds maximum allowed value" in str(exc_info.value)

    def test_create(self):
        """Test creating an IKE Gateway."""
        # Setup the mock
        self.mock_scm.post.return_value = MOCK_IKE_GATEWAY
        
        # Define input data
        data = {
            "name": "test-ike-gateway",
            "folder": "test-folder",
            "authentication": {
                "pre_shared_key": {
                    "key": "secret-key"
                }
            },
            "peer_id": {
                "type": "ipaddr",
                "id": "10.0.0.1"
            },
            "protocol": {
                "version": "ikev2",
                "ikev2": {
                    "ike_crypto_profile": "default",
                    "dpd": {
                        "enable": True
                    }
                }
            },
            "peer_address": {
                "ip": "10.0.0.1"
            }
        }
        
        # Call the method
        result = self.client.create(data)
        
        # Assertions
        self.mock_scm.post.assert_called_once()
        assert isinstance(result, IKEGatewayResponseModel)
        assert result.id == UUID("123e4567-e89b-12d3-a456-426655440000")
        assert result.name == "test-ike-gateway"

    def test_get(self):
        """Test getting an IKE Gateway by ID."""
        # Setup the mock
        self.mock_scm.get.return_value = MOCK_IKE_GATEWAY
        
        # Call the method
        result = self.client.get("123e4567-e89b-12d3-a456-426655440000")
        
        # Assertions
        self.mock_scm.get.assert_called_once_with(
            "/config/network/v1/ike-gateways/123e4567-e89b-12d3-a456-426655440000"
        )
        assert isinstance(result, IKEGatewayResponseModel)
        assert result.id == UUID("123e4567-e89b-12d3-a456-426655440000")
        assert result.name == "test-ike-gateway"

    def test_update(self):
        """Test updating an IKE Gateway."""
        # Setup the mock
        self.mock_scm.put.return_value = MOCK_IKE_GATEWAY
        
        # Create update model
        update_data = MOCK_IKE_GATEWAY.copy()
        update_model = IKEGatewayUpdateModel(**update_data)
        
        # Call the method
        result = self.client.update(update_model)
        
        # Assertions
        self.mock_scm.put.assert_called_once()
        assert isinstance(result, IKEGatewayResponseModel)
        assert result.id == UUID("123e4567-e89b-12d3-a456-426655440000")

    def test_delete(self):
        """Test deleting an IKE Gateway."""
        # Setup the mock
        self.mock_scm.delete.return_value = None
        
        # Call the method
        self.client.delete("123e4567-e89b-12d3-a456-426655440000")
        
        # Assertions
        self.mock_scm.delete.assert_called_once_with(
            "/config/network/v1/ike-gateways/123e4567-e89b-12d3-a456-426655440000"
        )

    def test_list_empty_folder(self):
        """Test list method with empty folder name."""
        with pytest.raises(MissingQueryParameterError) as exc_info:
            self.client.list(folder="")
        
        # Check the error details instead of the exact message
        assert "folder" in str(exc_info.value)
        assert "is not allowed to be empty" in str(exc_info.value)

    def test_list_no_container(self):
        """Test list method with no container specified."""
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list()
        
        # Check the error details instead of the exact message
        assert "Invalid container parameters" in str(exc_info.value)

    def test_list_multiple_containers(self):
        """Test list method with multiple containers specified."""
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="test-folder", snippet="test-snippet")
        
        # Check the error details instead of the exact message
        assert "Invalid container parameters" in str(exc_info.value)

    def test_list(self):
        """Test listing IKE Gateways."""
        # Setup mock response
        mock_gateway_1 = MOCK_IKE_GATEWAY.copy()
        mock_gateway_2 = MOCK_IKE_GATEWAY.copy()
        mock_gateway_2["id"] = "223e4567-e89b-12d3-a456-426655440000"
        mock_gateway_2["name"] = "test-gateway-2"
        
        self.mock_scm.get.return_value = {
            "data": [mock_gateway_1, mock_gateway_2],
            "limit": 2500,
            "offset": 0,
            "total": 2
        }
        
        # Call the method
        result = self.client.list(folder="test-folder")
        
        # Assertions
        self.mock_scm.get.assert_called_once()
        assert len(result) == 2
        assert isinstance(result[0], IKEGatewayResponseModel)
        assert result[0].id == UUID("123e4567-e89b-12d3-a456-426655440000")
        assert result[1].id == UUID("223e4567-e89b-12d3-a456-426655440000")

    def test_list_with_pagination(self):
        """Test listing IKE Gateways with pagination."""
        # Setup mock responses for pagination scenario
        mock_gateway_1 = MOCK_IKE_GATEWAY.copy()
        mock_gateway_2 = MOCK_IKE_GATEWAY.copy()
        mock_gateway_2["id"] = "223e4567-e89b-12d3-a456-426655440000"
        mock_gateway_2["name"] = "test-gateway-2"
        
        mock_gateway_3 = MOCK_IKE_GATEWAY.copy()
        mock_gateway_3["id"] = "323e4567-e89b-12d3-a456-426655440000"
        mock_gateway_3["name"] = "test-gateway-3"
        
        # First page response
        first_response = {
            "data": [mock_gateway_1, mock_gateway_2],
            "limit": 2,
            "offset": 0,
            "total": 3
        }
        
        # Second page response
        second_response = {
            "data": [mock_gateway_3],
            "limit": 2,
            "offset": 2,
            "total": 3
        }
        
        # Configure mock to return different responses for each call
        self.mock_scm.get.side_effect = [first_response, second_response]
        
        # Set a smaller limit for testing pagination
        self.client.max_limit = 2
        
        # Call the method
        result = self.client.list(folder="test-folder")
        
        # Assertions
        assert self.mock_scm.get.call_count == 2
        assert len(result) == 3
        assert result[0].id == UUID("123e4567-e89b-12d3-a456-426655440000")
        assert result[1].id == UUID("223e4567-e89b-12d3-a456-426655440000")
        assert result[2].id == UUID("323e4567-e89b-12d3-a456-426655440000")

    def test_list_with_exact_match(self):
        """Test listing IKE Gateways with exact_match=True."""
        # Setup mock response with different folder values
        mock_gateway_1 = MOCK_IKE_GATEWAY.copy()  # folder="test-folder"
        
        mock_gateway_2 = MOCK_IKE_GATEWAY.copy()
        mock_gateway_2["id"] = "223e4567-e89b-12d3-a456-426655440000"
        mock_gateway_2["name"] = "test-gateway-2"
        mock_gateway_2["folder"] = "other-folder"  # Different folder
        
        self.mock_scm.get.return_value = {
            "data": [mock_gateway_1, mock_gateway_2],
            "limit": 2500,
            "offset": 0,
            "total": 2
        }
        
        # Call the method with exact_match=True
        result = self.client.list(folder="test-folder", exact_match=True)
        
        # Assertions
        assert len(result) == 1  # Only the first gateway should match
        assert result[0].id == UUID("123e4567-e89b-12d3-a456-426655440000")

    def test_list_with_exclude_folders(self):
        """Test listing IKE Gateways with exclude_folders."""
        # Setup mock response with different folder values
        mock_gateway_1 = MOCK_IKE_GATEWAY.copy()
        mock_gateway_1["folder"] = "folder-1"
        
        mock_gateway_2 = MOCK_IKE_GATEWAY.copy()
        mock_gateway_2["id"] = "223e4567-e89b-12d3-a456-426655440000"
        mock_gateway_2["name"] = "test-gateway-2"
        mock_gateway_2["folder"] = "folder-2"  # To be excluded
        
        self.mock_scm.get.return_value = {
            "data": [mock_gateway_1, mock_gateway_2],
            "limit": 2500,
            "offset": 0,
            "total": 2
        }
        
        # Call the method with exclude_folders
        result = self.client.list(
            device="test-device",
            exclude_folders=["folder-2"]
        )
        
        # Assertions
        assert len(result) == 1  # Only the first gateway should be included
        assert result[0].id == UUID("123e4567-e89b-12d3-a456-426655440000")
        assert result[0].folder == "folder-1"
    
    def test_list_with_exclude_snippets(self):
        """Test listing IKE Gateways with exclude_snippets."""
        # Setup mock response with different snippet values
        mock_gateway_1 = MOCK_IKE_GATEWAY.copy()
        mock_gateway_1["snippet"] = "snippet-1"
        mock_gateway_1.pop("folder", None)  # Remove folder since we're using snippet
        
        mock_gateway_2 = MOCK_IKE_GATEWAY.copy()
        mock_gateway_2["id"] = "223e4567-e89b-12d3-a456-426655440000"
        mock_gateway_2["name"] = "test-gateway-2"
        mock_gateway_2["snippet"] = "snippet-2"  # To be excluded
        mock_gateway_2.pop("folder", None)  # Remove folder
        
        self.mock_scm.get.return_value = {
            "data": [mock_gateway_1, mock_gateway_2],
            "limit": 2500,
            "offset": 0,
            "total": 2
        }
        
        # Call the method with exclude_snippets
        result = self.client.list(
            device="test-device",
            exclude_snippets=["snippet-2"]
        )
        
        # Assertions
        assert len(result) == 1  # Only the first gateway should be included
        assert result[0].id == UUID("123e4567-e89b-12d3-a456-426655440000")
        assert result[0].snippet == "snippet-1"
    
    def test_list_with_exclude_devices(self):
        """Test listing IKE Gateways with exclude_devices."""
        # Setup mock response with different device values
        mock_gateway_1 = MOCK_IKE_GATEWAY.copy()
        mock_gateway_1["device"] = "device-1"
        mock_gateway_1.pop("folder", None)  # Remove folder since we're using device
        
        mock_gateway_2 = MOCK_IKE_GATEWAY.copy()
        mock_gateway_2["id"] = "223e4567-e89b-12d3-a456-426655440000"
        mock_gateway_2["name"] = "test-gateway-2"
        mock_gateway_2["device"] = "device-2"  # To be excluded
        mock_gateway_2.pop("folder", None)  # Remove folder
        
        self.mock_scm.get.return_value = {
            "data": [mock_gateway_1, mock_gateway_2],
            "limit": 2500,
            "offset": 0,
            "total": 2
        }
        
        # Call the method with exclude_devices
        result = self.client.list(
            folder="test-folder",
            exclude_devices=["device-2"]
        )
        
        # Assertions
        assert len(result) == 1  # Only the first gateway should be included
        assert result[0].id == UUID("123e4567-e89b-12d3-a456-426655440000")
        assert result[0].device == "device-1"

    def test_list_invalid_response_not_dict(self):
        """Test list method handling invalid response that's not a dictionary."""
        # Setup the mock to return a non-dictionary
        self.mock_scm.get.return_value = "not a dictionary"
        
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="test-folder")
        
        # Check the error details instead of the exact message
        assert "Response is not a dictionary" in str(exc_info.value)

    def test_list_missing_data_field(self):
        """Test list method handling response missing 'data' field."""
        # Setup the mock to return a dict without 'data'
        self.mock_scm.get.return_value = {"limit": 2500, "offset": 0, "total": 0}
        
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="test-folder")
        
        # Check the error details instead of the exact message
        assert "data" in str(exc_info.value)
        assert "field missing in the response" in str(exc_info.value)

    def test_list_data_not_list(self):
        """Test list method handling 'data' field that's not a list."""
        # Setup the mock to return a dict with non-list 'data'
        self.mock_scm.get.return_value = {"data": "not a list", "limit": 2500, "offset": 0}
        
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="test-folder")
        
        # Check the error details instead of the exact message
        assert "data" in str(exc_info.value)
        assert "field must be a list" in str(exc_info.value)

    def test_fetch_empty_name(self):
        """Test fetch method with empty name."""
        with pytest.raises(MissingQueryParameterError) as exc_info:
            self.client.fetch(name="", folder="test-folder")
        
        # Check the error details instead of the exact message
        assert "name" in str(exc_info.value)
        assert "is not allowed to be empty" in str(exc_info.value)

    def test_fetch_empty_folder(self):
        """Test fetch method with empty folder."""
        with pytest.raises(MissingQueryParameterError) as exc_info:
            self.client.fetch(name="test-gateway", folder="")
        
        # Check the error details instead of the exact message
        assert "folder" in str(exc_info.value)
        assert "is not allowed to be empty" in str(exc_info.value)

    def test_fetch_no_container(self):
        """Test fetch method with no container specified."""
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="test-gateway")
        
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided" in str(exc_info.value)

    def test_fetch_multiple_containers(self):
        """Test fetch method with multiple containers specified."""
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(
                name="test-gateway", 
                folder="test-folder", 
                snippet="test-snippet"
            )
        
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided" in str(exc_info.value)

    def test_fetch(self):
        """Test fetching an IKE Gateway by name."""
        # Setup the mock
        self.mock_scm.get.return_value = {"data": [MOCK_IKE_GATEWAY]}
        
        # Call the method
        result = self.client.fetch(name="test-ike-gateway", folder="test-folder")
        
        # Assertions
        self.mock_scm.get.assert_called_once()
        assert isinstance(result, IKEGatewayResponseModel)
        assert result.name == "test-ike-gateway"
        assert result.id == UUID("123e4567-e89b-12d3-a456-426655440000")

    def test_fetch_direct_response(self):
        """Test fetching when the API returns a direct object response."""
        # Setup the mock to return a direct object response
        self.mock_scm.get.return_value = MOCK_IKE_GATEWAY
        
        # Call the method
        result = self.client.fetch(name="test-ike-gateway", folder="test-folder")
        
        # Assertions
        assert isinstance(result, IKEGatewayResponseModel)
        assert result.id == UUID("123e4567-e89b-12d3-a456-426655440000")
        
    def test_fetch_invalid_response_not_dict(self):
        """Test fetch method with a non-dictionary response."""
        # Setup the mock
        self.mock_scm.get.return_value = "not a dictionary"
        
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="test-ike-gateway", folder="test-folder")
        
        # Check the error details
        assert "Response is not a dictionary" in str(exc_info.value)

    def test_fetch_invalid_response(self):
        """Test fetching with an invalid API response."""
        # Setup the mock
        self.mock_scm.get.return_value = {"data": []}
        
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="test-ike-gateway", folder="test-folder")
        
        # Check the error details instead of the exact message
        assert "Response missing required IKE Gateway data" in str(exc_info.value)