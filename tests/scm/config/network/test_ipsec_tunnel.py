"""Unit tests for the IPsec Tunnel class."""

from unittest.mock import MagicMock
import uuid

import pytest

from scm.config.network import IPsecTunnel
from scm.exceptions import InvalidObjectError, MissingQueryParameterError
from scm.models.network import (
    IPsecTunnelCreateModel,
    IPsecTunnelResponseModel,
    IPsecTunnelUpdateModel,
)


@pytest.fixture
def sample_ipsec_tunnel_dict():
    """Return a sample IPsec tunnel dictionary."""
    return {
        "id": str(uuid.uuid4()),
        "name": "test-tunnel",
        "folder": "Test Folder",
        "auto_key": {
            "ike_gateway": [{"name": "gw1"}],
            "ipsec_crypto_profile": "default-profile",
            "proxy_id": [
                {
                    "name": "proxy1",
                    "local": "10.0.0.0/24",
                    "remote": "192.168.0.0/24",
                }
            ],
        },
        "anti_replay": True,
        "copy_tos": False,
        "enable_gre_encapsulation": False,
        "tunnel_monitor": {
            "enable": True,
            "destination_ip": "10.0.0.1",
            "proxy_id": "proxy1",
        },
    }


@pytest.fixture
def sample_ipsec_tunnel_response(sample_ipsec_tunnel_dict):
    """Return a sample IPsecTunnelResponseModel."""
    return IPsecTunnelResponseModel(**sample_ipsec_tunnel_dict)


@pytest.mark.usefixtures("load_env")
class TestIPsecTunnelBase:
    """Base class for IPsecTunnel tests."""

    @pytest.fixture(autouse=True)
    def setup_method(self, mock_scm):
        """Setup method that runs before each test."""
        self.mock_scm = mock_scm
        self.mock_scm.get = MagicMock()
        self.mock_scm.post = MagicMock()
        self.mock_scm.put = MagicMock()
        self.mock_scm.delete = MagicMock()
        self.client = IPsecTunnel(self.mock_scm, max_limit=5000)


class TestIPsecTunnel(TestIPsecTunnelBase):
    """Test suite for IPsecTunnel class."""

    def test_init(self):
        """Test initialization of IPsecTunnel class."""
        ipsec_tunnel = IPsecTunnel(self.mock_scm)
        assert ipsec_tunnel.api_client == self.mock_scm
        assert ipsec_tunnel.ENDPOINT == "/config/network/v1/ipsec-tunnels"
        assert ipsec_tunnel.max_limit == ipsec_tunnel.DEFAULT_MAX_LIMIT

    def test_init_with_custom_max_limit(self):
        """Test initialization with custom max_limit."""
        ipsec_tunnel = IPsecTunnel(self.mock_scm, max_limit=1000)
        assert ipsec_tunnel.max_limit == 1000

    def test_init_with_invalid_max_limit(self):
        """Test initialization with invalid max_limit."""
        with pytest.raises(InvalidObjectError) as excinfo:
            IPsecTunnel(self.mock_scm, max_limit="invalid")
        assert "Invalid max_limit type" in str(excinfo.value)

    def test_init_with_negative_max_limit(self):
        """Test initialization with negative max_limit."""
        with pytest.raises(InvalidObjectError) as excinfo:
            IPsecTunnel(self.mock_scm, max_limit=-1)
        assert "Invalid max_limit value" in str(excinfo.value)

    def test_init_with_excessive_max_limit(self):
        """Test initialization with excessive max_limit."""
        with pytest.raises(InvalidObjectError) as excinfo:
            ipsec_tunnel = IPsecTunnel(self.mock_scm)
            ipsec_tunnel.max_limit = 10000
        assert "max_limit exceeds maximum allowed value" in str(excinfo.value)

    def test_create(self, sample_ipsec_tunnel_dict):
        """Test create method."""
        self.mock_scm.post.return_value = sample_ipsec_tunnel_dict

        # Create a copy without the ID for create operation
        create_data = sample_ipsec_tunnel_dict.copy()
        create_data.pop("id")

        result = self.client.create(create_data)

        # Check that correct API call was made
        self.mock_scm.post.assert_called_once()
        call_args = self.mock_scm.post.call_args
        assert call_args[0][0] == self.client.ENDPOINT

        # Check payload validation
        payload = call_args[1]["json"]
        # Should be deserialized from a IPsecTunnelCreateModel
        IPsecTunnelCreateModel(**payload)

        # Check result
        assert isinstance(result, IPsecTunnelResponseModel)
        assert result.name == sample_ipsec_tunnel_dict["name"]
        assert result.folder == sample_ipsec_tunnel_dict["folder"]

    def test_get(self, sample_ipsec_tunnel_dict):
        """Test get method."""
        self.mock_scm.get.return_value = sample_ipsec_tunnel_dict
        object_id = sample_ipsec_tunnel_dict["id"]

        result = self.client.get(object_id)

        # Check that correct API call was made
        expected_endpoint = f"{self.client.ENDPOINT}/{object_id}"
        self.mock_scm.get.assert_called_once_with(expected_endpoint)

        # Check result
        assert isinstance(result, IPsecTunnelResponseModel)
        assert result.id == uuid.UUID(object_id)
        assert result.name == sample_ipsec_tunnel_dict["name"]

    def test_update(self, sample_ipsec_tunnel_dict):
        """Test update method."""
        self.mock_scm.put.return_value = sample_ipsec_tunnel_dict
        object_id = sample_ipsec_tunnel_dict["id"]

        # Create update model
        update_model = IPsecTunnelUpdateModel(**sample_ipsec_tunnel_dict)

        result = self.client.update(update_model)

        # Check that correct API call was made
        expected_endpoint = f"{self.client.ENDPOINT}/{object_id}"
        self.mock_scm.put.assert_called_once()
        call_args = self.mock_scm.put.call_args
        assert call_args[0][0] == expected_endpoint

        # ID should not be in the payload since it's in the URL
        assert "id" not in call_args[1]["json"]

        # Check result
        assert isinstance(result, IPsecTunnelResponseModel)
        assert result.id == uuid.UUID(object_id)
        assert result.name == sample_ipsec_tunnel_dict["name"]

    def test_delete(self, sample_ipsec_tunnel_dict):
        """Test delete method."""
        object_id = sample_ipsec_tunnel_dict["id"]

        self.client.delete(object_id)

        # Check that correct API call was made
        expected_endpoint = f"{self.client.ENDPOINT}/{object_id}"
        self.mock_scm.delete.assert_called_once_with(expected_endpoint)

    def test_list(self, sample_ipsec_tunnel_dict):
        """Test list method."""
        self.mock_scm.get.return_value = {
            "data": [sample_ipsec_tunnel_dict],
            "limit": 20,
            "offset": 0,
            "total": 1,
        }

        result = self.client.list(folder="Test Folder")

        # Check that correct API call was made
        self.mock_scm.get.assert_called_once()
        call_args = self.mock_scm.get.call_args
        assert call_args[0][0] == self.client.ENDPOINT
        assert call_args[1]["params"]["folder"] == "Test Folder"

        # Check result
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], IPsecTunnelResponseModel)
        assert result[0].name == sample_ipsec_tunnel_dict["name"]

    def test_list_response_errors(self):
        """Test list method error handling for invalid responses."""
        # Test non-dictionary response
        self.mock_scm.get.return_value = ["not", "a", "dictionary"]
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.list(folder="Test Folder")
        assert "Response is not a dictionary" in str(excinfo.value)

        # Test missing data field
        self.mock_scm.get.return_value = {"no_data": "field"}
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.list(folder="Test Folder")
        assert '"data" field missing in the response' in str(excinfo.value)

        # Test data field not a list
        self.mock_scm.get.return_value = {"data": "not a list"}
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.list(folder="Test Folder")
        assert '"data" field must be a list' in str(excinfo.value)

    def test_list_pagination(self, sample_ipsec_tunnel_dict):
        """Test list method pagination."""
        # Create multiple pages of data
        tunnel1 = sample_ipsec_tunnel_dict.copy()
        tunnel1["id"] = str(uuid.uuid4())
        tunnel1["name"] = "tunnel1"

        tunnel2 = sample_ipsec_tunnel_dict.copy()
        tunnel2["id"] = str(uuid.uuid4())
        tunnel2["name"] = "tunnel2"

        # Mock responses for pagination
        self.mock_scm.get.side_effect = [
            # First page
            {"data": [tunnel1], "limit": 1, "offset": 0, "total": 2},
            # Second page
            {"data": [tunnel2], "limit": 1, "offset": 1, "total": 2},
            # Empty page (to end pagination)
            {"data": [], "limit": 1, "offset": 2, "total": 2},
        ]

        # Set a small limit to force pagination
        self.client.max_limit = 1
        result = self.client.list(folder="Test Folder")

        # Should have made 3 calls (2 pages + 1 empty page to end pagination)
        assert self.mock_scm.get.call_count == 3

        # We should get both tunnels in the result
        assert len(result) == 2
        tunnel_names = [t.name for t in result]
        assert "tunnel1" in tunnel_names
        assert "tunnel2" in tunnel_names

    def test_list_with_exclusions(self, sample_ipsec_tunnel_dict):
        """Test list method with exclusion filters."""
        # Create multiple tunnels with different containers
        tunnel1 = sample_ipsec_tunnel_dict.copy()
        tunnel1["id"] = str(uuid.uuid4())
        tunnel1["name"] = "tunnel1"
        tunnel1["folder"] = "Folder1"

        tunnel2 = sample_ipsec_tunnel_dict.copy()
        tunnel2["id"] = str(uuid.uuid4())
        tunnel2["name"] = "tunnel2"
        tunnel2["folder"] = "Folder2"

        tunnel3 = sample_ipsec_tunnel_dict.copy()
        tunnel3["id"] = str(uuid.uuid4())
        tunnel3["name"] = "tunnel3"
        tunnel3["folder"] = "Folder1"
        tunnel3["snippet"] = "Snippet1"

        tunnel4 = sample_ipsec_tunnel_dict.copy()
        tunnel4["id"] = str(uuid.uuid4())
        tunnel4["name"] = "tunnel4"
        tunnel4["folder"] = "Folder1"
        tunnel4["device"] = "Device1"

        self.mock_scm.get.return_value = {
            "data": [tunnel1, tunnel2, tunnel3, tunnel4],
            "limit": 100,
            "offset": 0,
            "total": 4,
        }

        # Test exact_match filter
        result = self.client.list(folder="Folder1", exact_match=True)
        assert len(result) == 3  # Should match tunnel1, tunnel3, tunnel4

        # Test exclude_folders filter
        result = self.client.list(folder="Folder1", exclude_folders=["Folder2"])
        assert len(result) == 3  # Should exclude only tunnel2

        # Test exclude_snippets filter
        result = self.client.list(folder="Folder1", exclude_snippets=["Snippet1"])
        assert len(result) == 3  # Should exclude tunnel3

        # Test exclude_devices filter
        result = self.client.list(folder="Folder1", exclude_devices=["Device1"])
        assert len(result) == 3  # Should exclude tunnel4

        # Test combining multiple exclusions
        result = self.client.list(
            folder="Folder1", exclude_snippets=["Snippet1"], exclude_devices=["Device1"]
        )
        assert len(result) == 2  # Should exclude tunnel3 and tunnel4

    def test_list_with_empty_folder(self):
        """Test list method with empty folder parameter."""
        with pytest.raises(MissingQueryParameterError) as excinfo:
            self.client.list(folder="")

        assert '"folder" is not allowed to be empty' in str(excinfo.value)

    def test_list_with_missing_container(self):
        """Test list method with missing container parameter."""
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.list()

        assert "Invalid container parameters" in str(excinfo.value)

    def test_list_with_multiple_containers(self):
        """Test list method with multiple container parameters."""
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.list(folder="Test Folder", snippet="Test Snippet")

        assert "Invalid container parameters" in str(excinfo.value)

    def test_list_filtering(self, sample_ipsec_tunnel_dict):
        """Test list method with filtering."""
        # Create two tunnel objects for filtering tests
        tunnel1 = sample_ipsec_tunnel_dict.copy()
        tunnel1["id"] = str(uuid.uuid4())
        tunnel1["name"] = "tunnel1"
        tunnel1["auto_key"] = {
            "ike_gateway": [{"name": "gw1"}],
            "ipsec_crypto_profile": "profile-a",
        }

        tunnel2 = sample_ipsec_tunnel_dict.copy()
        tunnel2["id"] = str(uuid.uuid4())
        tunnel2["name"] = "tunnel2"
        tunnel2["auto_key"] = {
            "ike_gateway": [{"name": "gw2"}],
            "ipsec_crypto_profile": "profile-b",
        }

        self.mock_scm.get.return_value = {
            "data": [tunnel1, tunnel2],
            "limit": 20,
            "offset": 0,
            "total": 2,
        }

        # Test filtering by ipsec_crypto_profile
        result = self.client.list(folder="Test Folder", ipsec_crypto_profile=["profile-a"])

        assert len(result) == 1
        assert result[0].name == "tunnel1"

        # Test filtering by ipsec_crypto_profile with multiple values
        result = self.client.list(
            folder="Test Folder", ipsec_crypto_profile=["profile-a", "profile-b"]
        )
        assert len(result) == 2

        # Test with invalid filter type for ipsec_crypto_profile
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.list(folder="Test Folder", ipsec_crypto_profile="not-a-list")
        assert "Invalid Object" in str(excinfo.value)

    def test_fetch(self, sample_ipsec_tunnel_dict):
        """Test fetch method."""
        self.mock_scm.get.return_value = sample_ipsec_tunnel_dict

        result = self.client.fetch(name="test-tunnel", folder="Test Folder")

        # Check that correct API call was made
        self.mock_scm.get.assert_called_once()
        call_args = self.mock_scm.get.call_args
        assert call_args[0][0] == self.client.ENDPOINT
        assert call_args[1]["params"]["name"] == "test-tunnel"
        assert call_args[1]["params"]["folder"] == "Test Folder"

        # Check result
        assert isinstance(result, IPsecTunnelResponseModel)
        assert result.name == sample_ipsec_tunnel_dict["name"]

    def test_fetch_with_empty_name(self):
        """Test fetch method with empty name parameter."""
        with pytest.raises(MissingQueryParameterError) as excinfo:
            self.client.fetch(name="", folder="Test Folder")

        assert '"name" is not allowed to be empty' in str(excinfo.value)

    def test_fetch_with_empty_folder(self):
        """Test fetch method with empty folder parameter."""
        with pytest.raises(MissingQueryParameterError) as excinfo:
            self.client.fetch(name="test-tunnel", folder="")

        assert '"folder" is not allowed to be empty' in str(excinfo.value)

    def test_fetch_with_missing_container(self):
        """Test fetch method with missing container parameter."""
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.fetch(name="test-tunnel")

        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided" in str(
            excinfo.value
        )

    def test_fetch_with_invalid_response(self):
        """Test fetch method with invalid response."""
        # Response without an ID field or data field
        self.mock_scm.get.return_value = {"name": "test-tunnel"}

        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.fetch(name="test-tunnel", folder="Test Folder")

        assert "Response has invalid structure" in str(excinfo.value)

    def test_fetch_response_errors(self):
        """Test fetch method error handling for invalid responses."""
        # Test non-dictionary response
        self.mock_scm.get.return_value = ["not", "a", "dictionary"]
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.fetch(name="test-tunnel", folder="Test Folder")
        assert "Response is not a dictionary" in str(excinfo.value)

        # Test valid data list-style response
        valid_uuid = str(uuid.uuid4())
        self.mock_scm.get.return_value = {
            "data": [
                {
                    "id": valid_uuid,
                    "name": "test-tunnel",
                    "auto_key": {
                        "ike_gateway": [{"name": "gw1"}],
                        "ipsec_crypto_profile": "default-profile",
                    },
                }
            ]
        }

        # Should now parse the first object in the data array without raising an exception
        result = self.client.fetch(name="test-tunnel", folder="Test Folder")
        assert isinstance(result, IPsecTunnelResponseModel)
        assert result.id == uuid.UUID(valid_uuid)
        assert result.name == "test-tunnel"

        # Test empty data list
        self.mock_scm.get.return_value = {"data": []}
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.fetch(name="test-tunnel", folder="Test Folder")
        assert "No matching IPsec tunnel found" in str(excinfo.value)

        # Test data item without id field
        self.mock_scm.get.return_value = {
            "data": [{"name": "test-tunnel", "folder": "Test Folder"}]
        }
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.fetch(name="test-tunnel", folder="Test Folder")
        assert "Response data item missing 'id' field" in str(excinfo.value)

    def test_fetch_with_original_response_format(self, sample_ipsec_tunnel_dict):
        """Test fetch method with original response format (direct object with id field)."""
        # Set up the mock response in the original format
        self.mock_scm.get.return_value = sample_ipsec_tunnel_dict

        # Call fetch and verify the result
        result = self.client.fetch(
            name=sample_ipsec_tunnel_dict["name"], folder=sample_ipsec_tunnel_dict["folder"]
        )

        # Verify that the response was correctly processed
        assert isinstance(result, IPsecTunnelResponseModel)
        assert result.id == uuid.UUID(sample_ipsec_tunnel_dict["id"])
        assert result.name == sample_ipsec_tunnel_dict["name"]
        assert result.folder == sample_ipsec_tunnel_dict["folder"]

        # Verify API call parameters
        self.mock_scm.get.assert_called_once()
        call_args = self.mock_scm.get.call_args
        assert call_args[0][0] == self.client.ENDPOINT
        assert call_args[1]["params"]["name"] == sample_ipsec_tunnel_dict["name"]
        assert call_args[1]["params"]["folder"] == sample_ipsec_tunnel_dict["folder"]

    def test_fetch_with_list_response_format(self, sample_ipsec_tunnel_dict):
        """Test fetch method with list response format (data array with objects)."""
        # Create a deep copy to avoid modifying the original
        tunnel_data = sample_ipsec_tunnel_dict.copy()

        # Set up the mock response in the list format (like list() method returns)
        self.mock_scm.get.return_value = {
            "data": [tunnel_data],
            "limit": 20,
            "offset": 0,
            "total": 1,
        }

        # Call fetch and verify the result
        result = self.client.fetch(name=tunnel_data["name"], folder=tunnel_data["folder"])

        # Verify that the response was correctly processed from the data array
        assert isinstance(result, IPsecTunnelResponseModel)
        assert result.id == uuid.UUID(tunnel_data["id"])
        assert result.name == tunnel_data["name"]
        assert result.folder == tunnel_data["folder"]

        # Verify API call parameters
        self.mock_scm.get.assert_called_once()
        call_args = self.mock_scm.get.call_args
        assert call_args[0][0] == self.client.ENDPOINT
        assert call_args[1]["params"]["name"] == tunnel_data["name"]
        assert call_args[1]["params"]["folder"] == tunnel_data["folder"]

    def test_fetch_with_multiple_objects_in_data(self, sample_ipsec_tunnel_dict, monkeypatch):
        """Test fetch method when data array contains multiple objects."""
        from unittest.mock import MagicMock

        # Create two tunnel dictionaries with different IDs and names
        tunnel1 = sample_ipsec_tunnel_dict.copy()
        tunnel1["id"] = str(uuid.uuid4())
        tunnel1["name"] = "tunnel1"

        tunnel2 = sample_ipsec_tunnel_dict.copy()
        tunnel2["id"] = str(uuid.uuid4())
        tunnel2["name"] = "tunnel2"

        # Set up the mock response with multiple objects in data array
        self.mock_scm.get.return_value = {
            "data": [tunnel1, tunnel2],
            "limit": 20,
            "offset": 0,
            "total": 2,
        }

        # Mock the logger.warning method
        mock_warning = MagicMock()
        monkeypatch.setattr(self.client.logger, "warning", mock_warning)

        # Call fetch and verify the result
        result = self.client.fetch(name=tunnel1["name"], folder=tunnel1["folder"])

        # Verify that ONLY the first object in the data array was used
        assert isinstance(result, IPsecTunnelResponseModel)
        assert result.id == uuid.UUID(tunnel1["id"])
        assert result.name == tunnel1["name"]
        assert result.folder == tunnel1["folder"]

        # Ensure we didn't get the second object
        assert result.name != tunnel2["name"]
        assert result.id != uuid.UUID(tunnel2["id"])

        # Verify that the warning was logged
        mock_warning.assert_called_once()
        call_args = mock_warning.call_args[0][0]
        assert "Multiple IPsec tunnels found" in call_args
