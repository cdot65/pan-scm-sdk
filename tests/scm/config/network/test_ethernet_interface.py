"""Unit tests for the Ethernet Interface class."""

import uuid
from unittest.mock import MagicMock

import pytest

from scm.config.network.ethernet_interface import EthernetInterface
from scm.exceptions import InvalidObjectError, MissingQueryParameterError
from scm.models.network.ethernet_interface import (
    EthernetInterfaceResponseModel,
    EthernetInterfaceUpdateModel,
)


@pytest.fixture
def sample_ethernet_dict():
    """Return a sample ethernet interface dictionary."""
    return {
        "id": str(uuid.uuid4()),
        "name": "$test-interface",
        "default_value": "ethernet1/1",
        "folder": "Test Folder",
        "comment": "Test ethernet interface",
        "link_speed": "1000",
        "link_duplex": "full",
        "link_state": "up",
        "layer3": {
            "ip": [{"name": "192.168.1.1/24"}],
            "mtu": 1500,
        },
    }


@pytest.mark.usefixtures("load_env")
class TestEthernetInterfaceBase:
    """Base class for EthernetInterface tests."""

    @pytest.fixture(autouse=True)
    def setup_method(self, mock_scm):
        """Setup method that runs before each test."""
        self.mock_scm = mock_scm
        self.mock_scm.get = MagicMock()
        self.mock_scm.post = MagicMock()
        self.mock_scm.put = MagicMock()
        self.mock_scm.delete = MagicMock()
        self.client = EthernetInterface(self.mock_scm, max_limit=5000)


class TestEthernetInterface(TestEthernetInterfaceBase):
    """Test suite for EthernetInterface class."""

    def test_init(self):
        """Test initialization of EthernetInterface class."""
        client = EthernetInterface(self.mock_scm)
        assert client.ENDPOINT == "/config/network/v1/ethernet-interfaces"
        assert client.max_limit == client.DEFAULT_MAX_LIMIT

    def test_init_with_invalid_max_limit(self):
        """Test initialization with invalid max_limit."""
        with pytest.raises(InvalidObjectError):
            EthernetInterface(self.mock_scm, max_limit="invalid")

    def test_create(self, sample_ethernet_dict):
        """Test create method."""
        self.mock_scm.post.return_value = sample_ethernet_dict
        create_data = {k: v for k, v in sample_ethernet_dict.items() if k != "id"}
        result = self.client.create(create_data)
        self.mock_scm.post.assert_called_once()
        assert isinstance(result, EthernetInterfaceResponseModel)
        assert result.name == sample_ethernet_dict["name"]

    def test_get(self, sample_ethernet_dict):
        """Test get method."""
        self.mock_scm.get.return_value = sample_ethernet_dict
        result = self.client.get(sample_ethernet_dict["id"])
        assert isinstance(result, EthernetInterfaceResponseModel)
        assert result.id == uuid.UUID(sample_ethernet_dict["id"])

    def test_update(self, sample_ethernet_dict):
        """Test update method."""
        self.mock_scm.put.return_value = sample_ethernet_dict
        update_model = EthernetInterfaceUpdateModel(**sample_ethernet_dict)
        result = self.client.update(update_model)
        self.mock_scm.put.assert_called_once()
        assert isinstance(result, EthernetInterfaceResponseModel)

    def test_delete(self, sample_ethernet_dict):
        """Test delete method."""
        self.client.delete(sample_ethernet_dict["id"])
        expected_endpoint = f"{self.client.ENDPOINT}/{sample_ethernet_dict['id']}"
        self.mock_scm.delete.assert_called_once_with(expected_endpoint)

    def test_list(self, sample_ethernet_dict):
        """Test list method."""
        self.mock_scm.get.return_value = {"data": [sample_ethernet_dict], "limit": 20, "offset": 0, "total": 1}
        result = self.client.list(folder="Test Folder")
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], EthernetInterfaceResponseModel)

    def test_list_with_empty_folder(self):
        """Test list method with empty folder."""
        with pytest.raises(MissingQueryParameterError):
            self.client.list(folder="")

    def test_list_with_missing_container(self):
        """Test list method with missing container."""
        with pytest.raises(InvalidObjectError):
            self.client.list()

    def test_list_filtering_by_mode(self, sample_ethernet_dict):
        """Test list method with mode filtering."""
        iface_l3 = sample_ethernet_dict.copy()
        iface_l3["id"] = str(uuid.uuid4())

        iface_l2 = {
            "id": str(uuid.uuid4()),
            "name": "$layer2-iface",
            "folder": "Test Folder",
            "layer2": {"vlan_tag": "100"},
        }

        iface_tap = {
            "id": str(uuid.uuid4()),
            "name": "$tap-iface",
            "folder": "Test Folder",
            "tap": {},
        }

        self.mock_scm.get.return_value = {"data": [iface_l3, iface_l2, iface_tap], "limit": 20, "offset": 0, "total": 3}

        result = self.client.list(folder="Test Folder", mode="layer3")
        assert len(result) == 1
        assert result[0].layer3 is not None

        result = self.client.list(folder="Test Folder", mode="layer2")
        assert len(result) == 1
        assert result[0].layer2 is not None

        result = self.client.list(folder="Test Folder", mode="tap")
        assert len(result) == 1
        assert result[0].tap is not None

    def test_list_filtering_by_link_speed(self, sample_ethernet_dict):
        """Test list method with link_speed filtering."""
        iface1 = sample_ethernet_dict.copy()
        iface1["id"] = str(uuid.uuid4())
        iface1["link_speed"] = "1000"

        iface2 = sample_ethernet_dict.copy()
        iface2["id"] = str(uuid.uuid4())
        iface2["name"] = "$other-iface"
        iface2["link_speed"] = "10000"

        self.mock_scm.get.return_value = {"data": [iface1, iface2], "limit": 20, "offset": 0, "total": 2}

        result = self.client.list(folder="Test Folder", link_speed="1000")
        assert len(result) == 1
        assert result[0].link_speed == "1000"

    def test_list_filtering_by_link_state(self, sample_ethernet_dict):
        """Test list method with link_state filtering."""
        iface1 = sample_ethernet_dict.copy()
        iface1["id"] = str(uuid.uuid4())
        iface1["link_state"] = "up"

        iface2 = sample_ethernet_dict.copy()
        iface2["id"] = str(uuid.uuid4())
        iface2["name"] = "$down-iface"
        iface2["link_state"] = "down"

        self.mock_scm.get.return_value = {"data": [iface1, iface2], "limit": 20, "offset": 0, "total": 2}

        result = self.client.list(folder="Test Folder", link_state="up")
        assert len(result) == 1
        assert result[0].link_state == "up"

    def test_fetch(self, sample_ethernet_dict):
        """Test fetch method."""
        self.mock_scm.get.return_value = sample_ethernet_dict
        result = self.client.fetch(name="$test-interface", folder="Test Folder")
        assert isinstance(result, EthernetInterfaceResponseModel)
        assert result.name == sample_ethernet_dict["name"]

    def test_fetch_with_empty_name(self):
        """Test fetch method with empty name."""
        with pytest.raises(MissingQueryParameterError):
            self.client.fetch(name="", folder="Test Folder")

    def test_fetch_with_missing_container(self):
        """Test fetch method with missing container."""
        with pytest.raises(InvalidObjectError):
            self.client.fetch(name="$test")

    def test_fetch_with_data_array_response(self, sample_ethernet_dict):
        """Test fetch method when API returns data in array format."""
        self.mock_scm.get.return_value = {"data": [sample_ethernet_dict]}
        result = self.client.fetch(name="$test-interface", folder="Test Folder")
        assert isinstance(result, EthernetInterfaceResponseModel)
        assert result.name == sample_ethernet_dict["name"]

    def test_fetch_not_found(self):
        """Test fetch method when interface is not found."""
        self.mock_scm.get.return_value = {"data": []}
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="nonexistent", folder="Test Folder")
        assert "not found" in exc_info.value.message.lower()


class TestEthernetInterfaceAdvanced(TestEthernetInterfaceBase):
    """Advanced test cases for EthernetInterface."""

    def test_create_layer2_interface(self):
        """Test creating a layer2 ethernet interface."""
        create_data = {
            "name": "$layer2-interface",
            "folder": "Test Folder",
            "layer2": {
                "vlan_tag": "100",
                "lldp": {"enable": True},
            },
        }
        response_data = {
            "id": str(uuid.uuid4()),
            **create_data,
        }
        self.mock_scm.post.return_value = response_data
        result = self.client.create(create_data)
        assert isinstance(result, EthernetInterfaceResponseModel)
        assert result.layer2 is not None
        assert result.layer2.vlan_tag == "100"

    def test_create_layer3_dhcp_interface(self):
        """Test creating a layer3 ethernet interface with DHCP."""
        create_data = {
            "name": "$dhcp-interface",
            "default_value": "ethernet1/1",
            "folder": "Test Folder",
            "layer3": {
                "dhcp_client": {
                    "enable": True,
                    "create_default_route": True,
                },
            },
        }
        response_data = {
            "id": str(uuid.uuid4()),
            **create_data,
        }
        self.mock_scm.post.return_value = response_data
        result = self.client.create(create_data)
        assert isinstance(result, EthernetInterfaceResponseModel)
        assert result.layer3 is not None
        assert result.layer3.dhcp_client is not None

    def test_create_tap_interface(self):
        """Test creating a TAP ethernet interface."""
        create_data = {
            "name": "$tap-interface",
            "folder": "Test Folder",
            "tap": {},
        }
        response_data = {
            "id": str(uuid.uuid4()),
            **create_data,
        }
        self.mock_scm.post.return_value = response_data
        result = self.client.create(create_data)
        assert isinstance(result, EthernetInterfaceResponseModel)
        assert result.tap is not None

    def test_create_with_poe(self):
        """Test creating an ethernet interface with PoE configuration."""
        create_data = {
            "name": "$poe-interface",
            "folder": "Test Folder",
            "poe": {
                "poe_enabled": True,
                "poe_rsvd_pwr": 30,
            },
        }
        response_data = {
            "id": str(uuid.uuid4()),
            **create_data,
        }
        self.mock_scm.post.return_value = response_data
        result = self.client.create(create_data)
        assert isinstance(result, EthernetInterfaceResponseModel)
        assert result.poe is not None
        assert result.poe.poe_enabled is True

    def test_list_with_exact_match(self, sample_ethernet_dict):
        """Test list method with exact_match."""
        iface1 = sample_ethernet_dict.copy()
        iface1["id"] = str(uuid.uuid4())
        iface1["folder"] = "Test Folder"

        iface2 = sample_ethernet_dict.copy()
        iface2["id"] = str(uuid.uuid4())
        iface2["name"] = "$other-iface"
        iface2["folder"] = "Other Folder"

        self.mock_scm.get.return_value = {"data": [iface1, iface2], "limit": 20, "offset": 0, "total": 2}

        result = self.client.list(folder="Test Folder", exact_match=True)
        assert len(result) == 1
        assert result[0].folder == "Test Folder"

    def test_list_with_exclude_folders(self, sample_ethernet_dict):
        """Test list method with exclude_folders."""
        iface1 = sample_ethernet_dict.copy()
        iface1["id"] = str(uuid.uuid4())
        iface1["folder"] = "Folder A"

        iface2 = sample_ethernet_dict.copy()
        iface2["id"] = str(uuid.uuid4())
        iface2["name"] = "$iface-b"
        iface2["folder"] = "Folder B"

        self.mock_scm.get.return_value = {"data": [iface1, iface2], "limit": 20, "offset": 0, "total": 2}

        result = self.client.list(folder="Folder A", exclude_folders=["Folder B"])
        assert len(result) == 1
        assert result[0].folder == "Folder A"
