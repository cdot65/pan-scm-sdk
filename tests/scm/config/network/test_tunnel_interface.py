"""Unit tests for the Tunnel Interface class."""

import uuid
from unittest.mock import MagicMock

import pytest

from scm.config.network.tunnel_interface import TunnelInterface
from scm.exceptions import InvalidObjectError, MissingQueryParameterError
from scm.models.network.tunnel_interface import (
    TunnelInterfaceCreateModel,
    TunnelInterfaceResponseModel,
    TunnelInterfaceUpdateModel,
)


@pytest.fixture
def sample_tunnel_dict():
    """Return a sample tunnel interface dictionary."""
    return {
        "id": str(uuid.uuid4()),
        "name": "tunnel.1",
        "folder": "Test Folder",
        "default_value": "tunnel.1",
        "comment": "Test tunnel interface",
        "mtu": 1500,
        "interface_management_profile": "default-mgmt",
        "ip": [{"name": "192.168.1.1/24"}],
    }


@pytest.fixture
def sample_tunnel_response(sample_tunnel_dict):
    """Return a sample TunnelInterfaceResponseModel."""
    return TunnelInterfaceResponseModel(**sample_tunnel_dict)


@pytest.mark.usefixtures("load_env")
class TestTunnelInterfaceBase:
    """Base class for TunnelInterface tests."""

    @pytest.fixture(autouse=True)
    def setup_method(self, mock_scm):
        """Setup method that runs before each test."""
        self.mock_scm = mock_scm
        self.mock_scm.get = MagicMock()
        self.mock_scm.post = MagicMock()
        self.mock_scm.put = MagicMock()
        self.mock_scm.delete = MagicMock()
        self.client = TunnelInterface(self.mock_scm, max_limit=5000)


class TestTunnelInterface(TestTunnelInterfaceBase):
    """Test suite for TunnelInterface class."""

    def test_init(self):
        """Test initialization of TunnelInterface class."""
        tunnel = TunnelInterface(self.mock_scm)
        assert tunnel.api_client == self.mock_scm
        assert tunnel.ENDPOINT == "/config/network/v1/tunnel-interfaces"
        assert tunnel.max_limit == tunnel.DEFAULT_MAX_LIMIT

    def test_init_with_custom_max_limit(self):
        """Test initialization with custom max_limit."""
        tunnel = TunnelInterface(self.mock_scm, max_limit=1000)
        assert tunnel.max_limit == 1000

    def test_init_with_invalid_max_limit(self):
        """Test initialization with invalid max_limit."""
        with pytest.raises(InvalidObjectError) as excinfo:
            TunnelInterface(self.mock_scm, max_limit="invalid")
        assert "Invalid max_limit type" in str(excinfo.value)

    def test_init_with_negative_max_limit(self):
        """Test initialization with negative max_limit."""
        with pytest.raises(InvalidObjectError) as excinfo:
            TunnelInterface(self.mock_scm, max_limit=-1)
        assert "Invalid max_limit value" in str(excinfo.value)

    def test_init_with_excessive_max_limit(self):
        """Test initialization with excessive max_limit."""
        with pytest.raises(InvalidObjectError) as excinfo:
            tunnel = TunnelInterface(self.mock_scm)
            tunnel.max_limit = 10000
        assert "max_limit exceeds maximum allowed value" in str(excinfo.value)

    def test_create(self, sample_tunnel_dict):
        """Test create method."""
        self.mock_scm.post.return_value = sample_tunnel_dict

        create_data = sample_tunnel_dict.copy()
        create_data.pop("id")

        result = self.client.create(create_data)

        self.mock_scm.post.assert_called_once()
        call_args = self.mock_scm.post.call_args
        assert call_args[0][0] == self.client.ENDPOINT

        payload = call_args[1]["json"]
        TunnelInterfaceCreateModel(**payload)

        assert isinstance(result, TunnelInterfaceResponseModel)
        assert result.name == sample_tunnel_dict["name"]
        assert result.folder == sample_tunnel_dict["folder"]

    def test_get(self, sample_tunnel_dict):
        """Test get method."""
        self.mock_scm.get.return_value = sample_tunnel_dict
        object_id = sample_tunnel_dict["id"]

        result = self.client.get(object_id)

        expected_endpoint = f"{self.client.ENDPOINT}/{object_id}"
        self.mock_scm.get.assert_called_once_with(expected_endpoint)

        assert isinstance(result, TunnelInterfaceResponseModel)
        assert result.id == uuid.UUID(object_id)
        assert result.name == sample_tunnel_dict["name"]

    def test_update(self, sample_tunnel_dict):
        """Test update method."""
        self.mock_scm.put.return_value = sample_tunnel_dict
        object_id = sample_tunnel_dict["id"]

        update_model = TunnelInterfaceUpdateModel(**sample_tunnel_dict)

        result = self.client.update(update_model)

        expected_endpoint = f"{self.client.ENDPOINT}/{object_id}"
        self.mock_scm.put.assert_called_once()
        call_args = self.mock_scm.put.call_args
        assert call_args[0][0] == expected_endpoint

        assert "id" not in call_args[1]["json"]

        assert isinstance(result, TunnelInterfaceResponseModel)
        assert result.id == uuid.UUID(object_id)
        assert result.name == sample_tunnel_dict["name"]

    def test_delete(self, sample_tunnel_dict):
        """Test delete method."""
        object_id = sample_tunnel_dict["id"]

        self.client.delete(object_id)

        expected_endpoint = f"{self.client.ENDPOINT}/{object_id}"
        self.mock_scm.delete.assert_called_once_with(expected_endpoint)

    def test_list(self, sample_tunnel_dict):
        """Test list method."""
        self.mock_scm.get.return_value = {
            "data": [sample_tunnel_dict],
            "limit": 20,
            "offset": 0,
            "total": 1,
        }

        result = self.client.list(folder="Test Folder")

        self.mock_scm.get.assert_called_once()
        call_args = self.mock_scm.get.call_args
        assert call_args[0][0] == self.client.ENDPOINT
        assert call_args[1]["params"]["folder"] == "Test Folder"

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TunnelInterfaceResponseModel)
        assert result[0].name == sample_tunnel_dict["name"]

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

    def test_list_pagination(self, sample_tunnel_dict):
        """Test list method pagination."""
        tunnel1 = sample_tunnel_dict.copy()
        tunnel1["id"] = str(uuid.uuid4())
        tunnel1["name"] = "tunnel.1"

        tunnel2 = sample_tunnel_dict.copy()
        tunnel2["id"] = str(uuid.uuid4())
        tunnel2["name"] = "tunnel.2"

        self.mock_scm.get.side_effect = [
            {"data": [tunnel1], "limit": 1, "offset": 0, "total": 2},
            {"data": [tunnel2], "limit": 1, "offset": 1, "total": 2},
            {"data": [], "limit": 1, "offset": 2, "total": 2},
        ]

        self.client.max_limit = 1
        result = self.client.list(folder="Test Folder")

        assert self.mock_scm.get.call_count == 3

        assert len(result) == 2
        names = [iface.name for iface in result]
        assert "tunnel.1" in names
        assert "tunnel.2" in names

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

    def test_list_filtering(self, sample_tunnel_dict):
        """Test list method with filtering."""
        tunnel1 = sample_tunnel_dict.copy()
        tunnel1["id"] = str(uuid.uuid4())
        tunnel1["name"] = "tunnel.1"
        tunnel1["mtu"] = 1500
        tunnel1["interface_management_profile"] = "profile1"

        tunnel2 = sample_tunnel_dict.copy()
        tunnel2["id"] = str(uuid.uuid4())
        tunnel2["name"] = "tunnel.2"
        tunnel2["mtu"] = 9000
        tunnel2["interface_management_profile"] = "profile2"

        self.mock_scm.get.return_value = {
            "data": [tunnel1, tunnel2],
            "limit": 20,
            "offset": 0,
            "total": 2,
        }

        # Filter by MTU
        result = self.client.list(folder="Test Folder", mtu=1500)
        assert len(result) == 1
        assert result[0].name == "tunnel.1"

        # Filter by interface_management_profile
        result = self.client.list(folder="Test Folder", interface_management_profile="profile2")
        assert len(result) == 1
        assert result[0].name == "tunnel.2"

        # Invalid MTU filter type
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.list(folder="Test Folder", mtu="not-an-int")
        assert "Invalid Object" in str(excinfo.value)

    def test_fetch(self, sample_tunnel_dict):
        """Test fetch method."""
        self.mock_scm.get.return_value = sample_tunnel_dict

        result = self.client.fetch(name="tunnel.1", folder="Test Folder")

        self.mock_scm.get.assert_called_once()
        call_args = self.mock_scm.get.call_args
        assert call_args[0][0] == self.client.ENDPOINT
        assert call_args[1]["params"]["name"] == "tunnel.1"
        assert call_args[1]["params"]["folder"] == "Test Folder"

        assert isinstance(result, TunnelInterfaceResponseModel)
        assert result.name == sample_tunnel_dict["name"]

    def test_fetch_with_empty_name(self):
        """Test fetch method with empty name parameter."""
        with pytest.raises(MissingQueryParameterError) as excinfo:
            self.client.fetch(name="", folder="Test Folder")
        assert '"name" is not allowed to be empty' in str(excinfo.value)

    def test_fetch_with_empty_folder(self):
        """Test fetch method with empty folder parameter."""
        with pytest.raises(MissingQueryParameterError) as excinfo:
            self.client.fetch(name="tunnel.1", folder="")
        assert '"folder" is not allowed to be empty' in str(excinfo.value)

    def test_fetch_with_missing_container(self):
        """Test fetch method with missing container parameter."""
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.fetch(name="tunnel.1")
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided" in str(
            excinfo.value
        )

    def test_fetch_with_invalid_response(self):
        """Test fetch method with invalid response."""
        self.mock_scm.get.return_value = {"name": "tunnel.1"}

        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.fetch(name="tunnel.1", folder="Test Folder")
        assert "Response has invalid structure" in str(excinfo.value)

    def test_fetch_response_errors(self):
        """Test fetch method error handling for invalid responses."""
        # Test non-dictionary response
        self.mock_scm.get.return_value = ["not", "a", "dictionary"]
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.fetch(name="tunnel.1", folder="Test Folder")
        assert "Response is not a dictionary" in str(excinfo.value)

        # Test valid data list-style response
        valid_uuid = str(uuid.uuid4())
        self.mock_scm.get.return_value = {"data": [{"id": valid_uuid, "name": "tunnel.1"}]}

        result = self.client.fetch(name="tunnel.1", folder="Test Folder")
        assert isinstance(result, TunnelInterfaceResponseModel)
        assert result.id == uuid.UUID(valid_uuid)

        # Test empty data list
        self.mock_scm.get.return_value = {"data": []}
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.fetch(name="tunnel.1", folder="Test Folder")
        assert "No matching tunnel interface found" in str(excinfo.value)
