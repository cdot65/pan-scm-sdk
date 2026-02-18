"""Unit tests for the DhcpInterface class."""

from unittest.mock import MagicMock
import uuid

import pytest

from scm.config.network import DhcpInterface
from scm.exceptions import InvalidObjectError, MissingQueryParameterError
from scm.models.network import (
    DhcpInterfaceCreateModel,
    DhcpInterfaceResponseModel,
    DhcpInterfaceUpdateModel,
)


@pytest.fixture
def sample_dhcp_interface_server_dict():
    """Return a sample DHCP interface dictionary with server configuration."""
    return {
        "id": str(uuid.uuid4()),
        "name": "ethernet1/1",
        "folder": "Test Folder",
        "server": {
            "mode": "auto",
            "probe_ip": True,
            "ip_pool": ["10.0.0.10-10.0.0.100"],
            "option": {
                "lease": {"timeout": 120},
                "gateway": "10.0.0.1",
                "subnet_mask": "255.255.255.0",
                "dns": {"primary": "8.8.8.8", "secondary": "8.8.4.4"},
            },
        },
    }


@pytest.fixture
def sample_dhcp_interface_relay_dict():
    """Return a sample DHCP interface dictionary with relay configuration."""
    return {
        "id": str(uuid.uuid4()),
        "name": "ethernet1/2",
        "folder": "Test Folder",
        "relay": {
            "ip": {
                "enabled": True,
                "server": ["10.0.0.1", "10.0.0.2"],
            },
        },
    }


@pytest.fixture
def sample_dhcp_interface_response(sample_dhcp_interface_server_dict):
    """Return a sample DhcpInterfaceResponseModel."""
    return DhcpInterfaceResponseModel(**sample_dhcp_interface_server_dict)


@pytest.mark.usefixtures("load_env")
class TestDhcpInterfaceBase:
    """Base class for DhcpInterface tests."""

    @pytest.fixture(autouse=True)
    def setup_method(self, mock_scm):
        """Setup method that runs before each test."""
        self.mock_scm = mock_scm
        self.mock_scm.get = MagicMock()
        self.mock_scm.post = MagicMock()
        self.mock_scm.put = MagicMock()
        self.mock_scm.delete = MagicMock()
        self.client = DhcpInterface(self.mock_scm, max_limit=5000)


class TestDhcpInterface(TestDhcpInterfaceBase):
    """Test suite for DhcpInterface class."""

    def test_init(self):
        """Test initialization of DhcpInterface class."""
        dhcp_interface = DhcpInterface(self.mock_scm)
        assert dhcp_interface.api_client == self.mock_scm
        assert dhcp_interface.ENDPOINT == "/config/network/v1/dhcp-interfaces"
        assert dhcp_interface.max_limit == dhcp_interface.DEFAULT_MAX_LIMIT

    def test_init_with_custom_max_limit(self):
        """Test initialization with custom max_limit."""
        dhcp_interface = DhcpInterface(self.mock_scm, max_limit=1000)
        assert dhcp_interface.max_limit == 1000

    def test_init_with_invalid_max_limit(self):
        """Test initialization with invalid max_limit."""
        with pytest.raises(InvalidObjectError) as excinfo:
            DhcpInterface(self.mock_scm, max_limit="invalid")
        assert "Invalid max_limit type" in str(excinfo.value)

    def test_init_with_negative_max_limit(self):
        """Test initialization with negative max_limit."""
        with pytest.raises(InvalidObjectError) as excinfo:
            DhcpInterface(self.mock_scm, max_limit=-1)
        assert "Invalid max_limit value" in str(excinfo.value)

    def test_init_with_excessive_max_limit(self):
        """Test initialization with excessive max_limit."""
        with pytest.raises(InvalidObjectError) as excinfo:
            dhcp_interface = DhcpInterface(self.mock_scm)
            dhcp_interface.max_limit = 10000
        assert "max_limit exceeds maximum allowed value" in str(excinfo.value)

    def test_create_server(self, sample_dhcp_interface_server_dict):
        """Test create method with server configuration."""
        self.mock_scm.post.return_value = sample_dhcp_interface_server_dict

        # Create a copy without the ID for create operation
        create_data = sample_dhcp_interface_server_dict.copy()
        create_data.pop("id")

        result = self.client.create(create_data)

        # Check that correct API call was made
        self.mock_scm.post.assert_called_once()
        call_args = self.mock_scm.post.call_args
        assert call_args[0][0] == self.client.ENDPOINT

        # Check payload validation
        payload = call_args[1]["json"]
        DhcpInterfaceCreateModel(**payload)

        # Check result
        assert isinstance(result, DhcpInterfaceResponseModel)
        assert result.name == sample_dhcp_interface_server_dict["name"]
        assert result.folder == sample_dhcp_interface_server_dict["folder"]
        assert result.server is not None
        assert result.server.mode.value == "auto"

    def test_create_relay(self, sample_dhcp_interface_relay_dict):
        """Test create method with relay configuration."""
        self.mock_scm.post.return_value = sample_dhcp_interface_relay_dict

        # Create a copy without the ID for create operation
        create_data = sample_dhcp_interface_relay_dict.copy()
        create_data.pop("id")

        result = self.client.create(create_data)

        # Check that correct API call was made
        self.mock_scm.post.assert_called_once()

        # Check result
        assert isinstance(result, DhcpInterfaceResponseModel)
        assert result.name == sample_dhcp_interface_relay_dict["name"]
        assert result.relay is not None
        assert result.relay.ip.enabled is True

    def test_get(self, sample_dhcp_interface_server_dict):
        """Test get method raises NotImplementedError due to SCM API limitation."""
        object_id = sample_dhcp_interface_server_dict["id"]

        with pytest.raises(NotImplementedError) as excinfo:
            self.client.get(object_id)

        assert "does not currently support" in str(excinfo.value)

        # Verify no API call was made
        self.mock_scm.get.assert_not_called()

    def test_update(self, sample_dhcp_interface_server_dict):
        """Test update method raises NotImplementedError due to SCM API limitation."""
        # Create update model
        update_model = DhcpInterfaceUpdateModel(**sample_dhcp_interface_server_dict)

        with pytest.raises(NotImplementedError) as excinfo:
            self.client.update(update_model)

        assert "does not currently support" in str(excinfo.value)

        # Verify no API call was made
        self.mock_scm.put.assert_not_called()

    def test_delete(self, sample_dhcp_interface_server_dict):
        """Test delete method raises NotImplementedError due to SCM API limitation."""
        object_id = sample_dhcp_interface_server_dict["id"]

        with pytest.raises(NotImplementedError) as excinfo:
            self.client.delete(object_id)

        assert "does not currently support" in str(excinfo.value)

        # Verify no API call was made
        self.mock_scm.delete.assert_not_called()

    def test_list(self, sample_dhcp_interface_server_dict):
        """Test list method."""
        self.mock_scm.get.return_value = {
            "data": [sample_dhcp_interface_server_dict],
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
        assert isinstance(result[0], DhcpInterfaceResponseModel)
        assert result[0].name == sample_dhcp_interface_server_dict["name"]

    def test_list_response_errors(self):
        """Test list method error handling for invalid responses."""
        # Test non-list, non-dict response (e.g., integer)
        self.mock_scm.get.return_value = 12345
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.list(folder="Test Folder")
        assert "Response is not a list or dictionary" in str(excinfo.value)

        # Test dict response missing 'data' field
        self.mock_scm.get.return_value = {"no_data": "field"}
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.list(folder="Test Folder")
        assert "Response is not a list or dictionary with 'data' field" in str(excinfo.value)

        # Test data field not a list
        self.mock_scm.get.return_value = {"data": "not a list"}
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.list(folder="Test Folder")
        assert '"data" field must be a list' in str(excinfo.value)

    def test_list_pagination(self, sample_dhcp_interface_server_dict):
        """Test list method pagination."""
        # Create multiple pages of data
        iface1 = sample_dhcp_interface_server_dict.copy()
        iface1["id"] = str(uuid.uuid4())
        iface1["name"] = "ethernet1/1"

        iface2 = sample_dhcp_interface_server_dict.copy()
        iface2["id"] = str(uuid.uuid4())
        iface2["name"] = "ethernet1/2"

        # Mock responses for pagination
        self.mock_scm.get.side_effect = [
            # First page
            {"data": [iface1], "limit": 1, "offset": 0, "total": 2},
            # Second page
            {"data": [iface2], "limit": 1, "offset": 1, "total": 2},
            # Empty page (to end pagination)
            {"data": [], "limit": 1, "offset": 2, "total": 2},
        ]

        # Set a small limit to force pagination
        self.client.max_limit = 1
        result = self.client.list(folder="Test Folder")

        # Should have made 3 calls (2 pages + 1 empty page to end pagination)
        assert self.mock_scm.get.call_count == 3

        # We should get both interfaces in the result
        assert len(result) == 2
        iface_names = [iface.name for iface in result]
        assert "ethernet1/1" in iface_names
        assert "ethernet1/2" in iface_names

    def test_list_with_exclusions(self, sample_dhcp_interface_server_dict):
        """Test list method with exclusion filters."""
        # Create multiple interfaces with different containers
        iface1 = sample_dhcp_interface_server_dict.copy()
        iface1["id"] = str(uuid.uuid4())
        iface1["name"] = "ethernet1/1"
        iface1["folder"] = "Folder1"

        iface2 = sample_dhcp_interface_server_dict.copy()
        iface2["id"] = str(uuid.uuid4())
        iface2["name"] = "ethernet1/2"
        iface2["folder"] = "Folder2"

        iface3 = sample_dhcp_interface_server_dict.copy()
        iface3["id"] = str(uuid.uuid4())
        iface3["name"] = "ethernet1/3"
        iface3["folder"] = "Folder1"
        iface3["snippet"] = "Snippet1"

        iface4 = sample_dhcp_interface_server_dict.copy()
        iface4["id"] = str(uuid.uuid4())
        iface4["name"] = "ethernet1/4"
        iface4["folder"] = "Folder1"
        iface4["device"] = "Device1"

        self.mock_scm.get.return_value = {
            "data": [iface1, iface2, iface3, iface4],
            "limit": 100,
            "offset": 0,
            "total": 4,
        }

        # Test exact_match filter
        result = self.client.list(folder="Folder1", exact_match=True)
        assert len(result) == 3  # Should match iface1, iface3, iface4

        # Test exclude_folders filter
        result = self.client.list(folder="Folder1", exclude_folders=["Folder2"])
        assert len(result) == 3  # Should exclude only iface2

        # Test exclude_snippets filter
        result = self.client.list(folder="Folder1", exclude_snippets=["Snippet1"])
        assert len(result) == 3  # Should exclude iface3

        # Test exclude_devices filter
        result = self.client.list(folder="Folder1", exclude_devices=["Device1"])
        assert len(result) == 3  # Should exclude iface4

        # Test combining multiple exclusions
        result = self.client.list(
            folder="Folder1", exclude_snippets=["Snippet1"], exclude_devices=["Device1"]
        )
        assert len(result) == 2  # Should exclude iface3 and iface4

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

    def test_list_filtering_by_mode(self, sample_dhcp_interface_server_dict):
        """Test list method with mode filtering."""
        # Create two interface objects for filtering tests
        iface1 = sample_dhcp_interface_server_dict.copy()
        iface1["id"] = str(uuid.uuid4())
        iface1["name"] = "ethernet1/1"
        iface1["server"] = {"mode": "auto", "ip_pool": ["10.0.0.10-10.0.0.100"]}

        iface2 = sample_dhcp_interface_server_dict.copy()
        iface2["id"] = str(uuid.uuid4())
        iface2["name"] = "ethernet1/2"
        iface2["server"] = {"mode": "enabled", "ip_pool": ["10.0.1.10-10.0.1.100"]}

        self.mock_scm.get.return_value = {
            "data": [iface1, iface2],
            "limit": 20,
            "offset": 0,
            "total": 2,
        }

        # Test filtering by mode
        result = self.client.list(folder="Test Folder", mode=["auto"])

        assert len(result) == 1
        assert result[0].name == "ethernet1/1"

        # Test with invalid filter type for mode
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.list(folder="Test Folder", mode="auto")  # Should be a list
        assert "Invalid Object" in str(excinfo.value)

    def test_fetch(self, sample_dhcp_interface_server_dict):
        """Test fetch method."""
        self.mock_scm.get.return_value = sample_dhcp_interface_server_dict

        result = self.client.fetch(name="ethernet1/1", folder="Test Folder")

        # Check that correct API call was made
        self.mock_scm.get.assert_called_once()
        call_args = self.mock_scm.get.call_args
        assert call_args[0][0] == self.client.ENDPOINT
        assert call_args[1]["params"]["name"] == "ethernet1/1"
        assert call_args[1]["params"]["folder"] == "Test Folder"

        # Check result
        assert isinstance(result, DhcpInterfaceResponseModel)
        assert result.name == sample_dhcp_interface_server_dict["name"]

    def test_fetch_with_empty_name(self):
        """Test fetch method with empty name parameter."""
        with pytest.raises(MissingQueryParameterError) as excinfo:
            self.client.fetch(name="", folder="Test Folder")

        assert '"name" is not allowed to be empty' in str(excinfo.value)

    def test_fetch_with_empty_folder(self):
        """Test fetch method with empty folder parameter."""
        with pytest.raises(MissingQueryParameterError) as excinfo:
            self.client.fetch(name="ethernet1/1", folder="")

        assert '"folder" is not allowed to be empty' in str(excinfo.value)

    def test_fetch_with_missing_container(self):
        """Test fetch method with missing container parameter."""
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.fetch(name="ethernet1/1")

        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided" in str(
            excinfo.value
        )

    def test_fetch_with_invalid_response(self):
        """Test fetch method with invalid response."""
        # Response without an ID field or data field
        self.mock_scm.get.return_value = {"name": "ethernet1/1"}

        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.fetch(name="ethernet1/1", folder="Test Folder")

        assert "Response has invalid structure" in str(excinfo.value)

    def test_fetch_response_errors(self):
        """Test fetch method error handling for invalid responses."""
        # Test non-list, non-dict response (e.g., integer)
        self.mock_scm.get.return_value = 12345
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.fetch(name="ethernet1/1", folder="Test Folder")
        assert "Response is not a dictionary or list" in str(excinfo.value)

        # Test valid data list-style response
        valid_uuid = str(uuid.uuid4())
        self.mock_scm.get.return_value = {"data": [{"id": valid_uuid, "name": "ethernet1/1"}]}

        # Should now parse the first object in the data array without raising an exception
        result = self.client.fetch(name="ethernet1/1", folder="Test Folder")
        assert isinstance(result, DhcpInterfaceResponseModel)
        assert result.id == uuid.UUID(valid_uuid)
        assert result.name == "ethernet1/1"

        # Test empty data list
        self.mock_scm.get.return_value = {"data": []}
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.fetch(name="ethernet1/1", folder="Test Folder")
        assert "No matching DHCP interface found" in str(excinfo.value)

        # Test data item without id field
        self.mock_scm.get.return_value = {
            "data": [{"name": "ethernet1/1", "folder": "Test Folder"}]
        }
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.fetch(name="ethernet1/1", folder="Test Folder")
        assert "Response data item missing 'id' field" in str(excinfo.value)

    def test_fetch_with_original_response_format(self, sample_dhcp_interface_server_dict):
        """Test fetch method with original response format (direct object with id field)."""
        # Set up the mock response in the original format
        self.mock_scm.get.return_value = sample_dhcp_interface_server_dict

        # Call fetch and verify the result
        result = self.client.fetch(
            name=sample_dhcp_interface_server_dict["name"],
            folder=sample_dhcp_interface_server_dict["folder"],
        )

        # Verify that the response was correctly processed
        assert isinstance(result, DhcpInterfaceResponseModel)
        assert result.id == uuid.UUID(sample_dhcp_interface_server_dict["id"])
        assert result.name == sample_dhcp_interface_server_dict["name"]
        assert result.folder == sample_dhcp_interface_server_dict["folder"]

        # Verify API call parameters
        self.mock_scm.get.assert_called_once()
        call_args = self.mock_scm.get.call_args
        assert call_args[0][0] == self.client.ENDPOINT
        assert call_args[1]["params"]["name"] == sample_dhcp_interface_server_dict["name"]
        assert call_args[1]["params"]["folder"] == sample_dhcp_interface_server_dict["folder"]

    def test_fetch_with_list_response_format(self, sample_dhcp_interface_server_dict):
        """Test fetch method with list response format (data array with objects)."""
        # Create a deep copy to avoid modifying the original
        iface_data = sample_dhcp_interface_server_dict.copy()

        # Set up the mock response in the list format (like list() method returns)
        self.mock_scm.get.return_value = {
            "data": [iface_data],
            "limit": 20,
            "offset": 0,
            "total": 1,
        }

        # Call fetch and verify the result
        result = self.client.fetch(name=iface_data["name"], folder=iface_data["folder"])

        # Verify that the response was correctly processed from the data array
        assert isinstance(result, DhcpInterfaceResponseModel)
        assert result.id == uuid.UUID(iface_data["id"])
        assert result.name == iface_data["name"]
        assert result.folder == iface_data["folder"]

        # Verify API call parameters
        self.mock_scm.get.assert_called_once()
        call_args = self.mock_scm.get.call_args
        assert call_args[0][0] == self.client.ENDPOINT
        assert call_args[1]["params"]["name"] == iface_data["name"]
        assert call_args[1]["params"]["folder"] == iface_data["folder"]

    def test_fetch_with_multiple_objects_in_data(
        self, sample_dhcp_interface_server_dict, monkeypatch
    ):
        """Test fetch method when data array contains multiple objects."""
        from unittest.mock import MagicMock

        # Create two interface dictionaries with different IDs and names
        iface1 = sample_dhcp_interface_server_dict.copy()
        iface1["id"] = str(uuid.uuid4())
        iface1["name"] = "ethernet1/1"

        iface2 = sample_dhcp_interface_server_dict.copy()
        iface2["id"] = str(uuid.uuid4())
        iface2["name"] = "ethernet1/2"

        # Set up the mock response with multiple objects in data array
        self.mock_scm.get.return_value = {
            "data": [iface1, iface2],
            "limit": 20,
            "offset": 0,
            "total": 2,
        }

        # Mock the logger.warning method
        mock_warning = MagicMock()
        monkeypatch.setattr(self.client.logger, "warning", mock_warning)

        # Call fetch and verify the result
        result = self.client.fetch(name=iface1["name"], folder=iface1["folder"])

        # Verify that ONLY the first object in the data array was used
        assert isinstance(result, DhcpInterfaceResponseModel)
        assert result.id == uuid.UUID(iface1["id"])
        assert result.name == iface1["name"]
        assert result.folder == iface1["folder"]

        # Ensure we didn't get the second object
        assert result.name != iface2["name"]
        assert result.id != uuid.UUID(iface2["id"])

        # Verify that the warning was logged
        mock_warning.assert_called_once()
        call_args = mock_warning.call_args[0][0]
        assert "Multiple DHCP interfaces found" in call_args

    def test_list_with_raw_array_response(self, sample_dhcp_interface_server_dict):
        """Test list method when API returns a raw array instead of {"data": [...]}."""
        self.mock_scm.get.return_value = [sample_dhcp_interface_server_dict]

        result = self.client.list(folder="Test Folder")

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], DhcpInterfaceResponseModel)
        assert result[0].name == sample_dhcp_interface_server_dict["name"]

    def test_fetch_with_raw_array_response(self, sample_dhcp_interface_server_dict):
        """Test fetch method when API returns a raw array instead of a dict."""
        self.mock_scm.get.return_value = [sample_dhcp_interface_server_dict]

        result = self.client.fetch(name="ethernet1/1", folder="Test Folder")

        assert isinstance(result, DhcpInterfaceResponseModel)
        assert result.name == sample_dhcp_interface_server_dict["name"]
        assert result.id == uuid.UUID(sample_dhcp_interface_server_dict["id"])

    def test_fetch_with_empty_raw_array(self):
        """Test fetch method when API returns an empty raw array."""
        self.mock_scm.get.return_value = []

        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.fetch(name="ethernet1/1", folder="Test Folder")
        assert "No matching DHCP interface found" in str(excinfo.value)

    def test_fetch_with_multiple_raw_array_items(
        self, sample_dhcp_interface_server_dict, monkeypatch
    ):
        """Test fetch method when API returns multiple items in raw array."""
        from unittest.mock import MagicMock

        iface1 = sample_dhcp_interface_server_dict.copy()
        iface1["id"] = str(uuid.uuid4())
        iface2 = sample_dhcp_interface_server_dict.copy()
        iface2["id"] = str(uuid.uuid4())

        self.mock_scm.get.return_value = [iface1, iface2]

        mock_warning = MagicMock()
        monkeypatch.setattr(self.client.logger, "warning", mock_warning)

        result = self.client.fetch(name="ethernet1/1", folder="Test Folder")

        assert isinstance(result, DhcpInterfaceResponseModel)
        assert result.id == uuid.UUID(iface1["id"])
        mock_warning.assert_called_once()
