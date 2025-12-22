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


class TestEthernetInterfaceEdgeCases(TestEthernetInterfaceBase):
    """Edge case tests for 100% coverage."""

    def test_max_limit_setter(self):
        """Test max_limit setter property."""
        self.client.max_limit = 1000
        assert self.client.max_limit == 1000

    def test_max_limit_less_than_one(self):
        """Test max_limit validation when less than 1."""
        with pytest.raises(InvalidObjectError) as exc_info:
            EthernetInterface(self.mock_scm, max_limit=0)
        assert "must be greater than 0" in exc_info.value.message

    def test_max_limit_exceeds_absolute_max(self):
        """Test max_limit validation when exceeding absolute max."""
        with pytest.raises(InvalidObjectError) as exc_info:
            EthernetInterface(self.mock_scm, max_limit=10000)
        assert "cannot exceed" in exc_info.value.message

    def test_list_mode_filter_invalid_type(self, sample_ethernet_dict):
        """Test list with invalid mode filter type."""
        self.mock_scm.get.return_value = {"data": [sample_ethernet_dict], "limit": 20, "offset": 0, "total": 1}
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="Test", mode=123)
        assert "'mode' filter must be a string" in exc_info.value.message

    def test_list_link_speed_filter_invalid_type(self, sample_ethernet_dict):
        """Test list with invalid link_speed filter type."""
        self.mock_scm.get.return_value = {"data": [sample_ethernet_dict], "limit": 20, "offset": 0, "total": 1}
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="Test", link_speed=123)
        assert "'link_speed' filter must be a string" in exc_info.value.message

    def test_list_link_state_filter_invalid_type(self, sample_ethernet_dict):
        """Test list with invalid link_state filter type."""
        self.mock_scm.get.return_value = {"data": [sample_ethernet_dict], "limit": 20, "offset": 0, "total": 1}
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="Test", link_state=123)
        assert "'link_state' filter must be a string" in exc_info.value.message

    def test_list_response_not_dict(self):
        """Test list when response is not a dictionary."""
        self.mock_scm.get.return_value = "invalid response"
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="Test")
        assert "expected dictionary" in exc_info.value.message

    def test_list_response_missing_data_field(self):
        """Test list when response missing data field."""
        self.mock_scm.get.return_value = {"other": "value"}
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="Test")
        assert "missing 'data' field" in exc_info.value.message

    def test_list_response_data_not_list(self):
        """Test list when data field is not a list."""
        self.mock_scm.get.return_value = {"data": "not a list"}
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="Test")
        assert "'data' field must be a list" in exc_info.value.message

    def test_list_pagination(self, sample_ethernet_dict):
        """Test list with pagination (multiple pages)."""
        # Create first page with exactly max_limit items to trigger pagination
        page1_data = []
        for i in range(5000):  # Use client's max_limit which is 5000
            item = sample_ethernet_dict.copy()
            item["id"] = str(uuid.uuid4())
            item["name"] = f"$iface-{i}"
            page1_data.append(item)

        page2_data = [sample_ethernet_dict.copy()]
        page2_data[0]["id"] = str(uuid.uuid4())
        page2_data[0]["name"] = "$iface-last"

        self.mock_scm.get.side_effect = [
            {"data": page1_data, "limit": 5000, "offset": 0, "total": 5001},
            {"data": page2_data, "limit": 5000, "offset": 5000, "total": 5001},
        ]

        result = self.client.list(folder="Test")
        assert len(result) == 5001
        assert self.mock_scm.get.call_count == 2

    def test_list_with_exclude_snippets(self, sample_ethernet_dict):
        """Test list with exclude_snippets filter."""
        iface1 = sample_ethernet_dict.copy()
        iface1["id"] = str(uuid.uuid4())
        iface1["snippet"] = "Snippet A"
        iface1["folder"] = None

        iface2 = sample_ethernet_dict.copy()
        iface2["id"] = str(uuid.uuid4())
        iface2["name"] = "$iface-b"
        iface2["snippet"] = "Snippet B"
        iface2["folder"] = None

        self.mock_scm.get.return_value = {"data": [iface1, iface2], "limit": 20, "offset": 0, "total": 2}

        result = self.client.list(snippet="Snippet A", exclude_snippets=["Snippet B"])
        assert len(result) == 1
        assert result[0].snippet == "Snippet A"

    def test_list_with_exclude_devices(self, sample_ethernet_dict):
        """Test list with exclude_devices filter."""
        iface1 = sample_ethernet_dict.copy()
        iface1["id"] = str(uuid.uuid4())
        iface1["device"] = "Device A"
        iface1["folder"] = None

        iface2 = sample_ethernet_dict.copy()
        iface2["id"] = str(uuid.uuid4())
        iface2["name"] = "$iface-b"
        iface2["device"] = "Device B"
        iface2["folder"] = None

        self.mock_scm.get.return_value = {"data": [iface1, iface2], "limit": 20, "offset": 0, "total": 2}

        result = self.client.list(device="Device A", exclude_devices=["Device B"])
        assert len(result) == 1
        assert result[0].device == "Device A"

    def test_fetch_empty_folder(self):
        """Test fetch with empty folder string."""
        with pytest.raises(MissingQueryParameterError) as exc_info:
            self.client.fetch(name="$test", folder="")
        assert "'folder' cannot be empty" in exc_info.value.message

    def test_fetch_response_not_dict(self):
        """Test fetch when response is not a dictionary."""
        self.mock_scm.get.return_value = "invalid"
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="$test", folder="Test")
        assert "expected dictionary" in exc_info.value.message

    def test_fetch_data_item_missing_id(self):
        """Test fetch when data item is missing id field."""
        self.mock_scm.get.return_value = {"data": [{"name": "$test"}]}
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="$test", folder="Test")
        assert "missing 'id' field" in exc_info.value.message

    def test_fetch_multiple_results_warning(self, sample_ethernet_dict, caplog):
        """Test fetch logs warning when multiple results found."""
        item1 = sample_ethernet_dict.copy()
        item1["id"] = str(uuid.uuid4())
        item2 = sample_ethernet_dict.copy()
        item2["id"] = str(uuid.uuid4())

        self.mock_scm.get.return_value = {"data": [item1, item2]}

        import logging
        with caplog.at_level(logging.WARNING, logger="scm.config.network.ethernet_interface"):
            result = self.client.fetch(name="$test-interface", folder="Test")

        assert result is not None
        assert "Multiple ethernet interfaces found" in caplog.text

    def test_fetch_invalid_response_format(self):
        """Test fetch with invalid response format (no id or data)."""
        self.mock_scm.get.return_value = {"other_field": "value"}
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="$test", folder="Test")
        assert "expected either 'id' or 'data' field" in exc_info.value.message
