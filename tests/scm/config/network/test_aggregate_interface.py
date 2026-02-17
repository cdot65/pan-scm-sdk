"""Unit tests for the Aggregate Interface class."""

import uuid
from unittest.mock import MagicMock

import pytest

from scm.config.network.aggregate_interface import AggregateInterface
from scm.exceptions import InvalidObjectError, MissingQueryParameterError
from scm.models.network.aggregate_interface import (
    AggregateInterfaceResponseModel,
    AggregateInterfaceUpdateModel,
)


@pytest.fixture
def sample_aggregate_dict():
    """Return a sample aggregate interface dictionary."""
    return {
        "id": str(uuid.uuid4()),
        "name": "ae1",
        "folder": "Test Folder",
        "comment": "Test aggregate interface",
        "layer3": {
            "ip": [{"name": "192.168.1.1/24"}],
            "mtu": 1500,
            "lacp": {"enable": True, "mode": "active"},
        },
    }


@pytest.mark.usefixtures("load_env")
class TestAggregateInterfaceBase:
    """Base class for AggregateInterface tests."""

    @pytest.fixture(autouse=True)
    def setup_method(self, mock_scm):
        """Setup method that runs before each test."""
        self.mock_scm = mock_scm
        self.mock_scm.get = MagicMock()
        self.mock_scm.post = MagicMock()
        self.mock_scm.put = MagicMock()
        self.mock_scm.delete = MagicMock()
        self.client = AggregateInterface(self.mock_scm, max_limit=5000)


class TestAggregateInterface(TestAggregateInterfaceBase):
    """Test suite for AggregateInterface class."""

    def test_init(self):
        """Test initialization of AggregateInterface class."""
        client = AggregateInterface(self.mock_scm)
        assert client.ENDPOINT == "/config/network/v1/aggregate-interfaces"
        assert client.max_limit == client.DEFAULT_MAX_LIMIT

    def test_init_with_invalid_max_limit(self):
        """Test initialization with invalid max_limit."""
        with pytest.raises(InvalidObjectError):
            AggregateInterface(self.mock_scm, max_limit="invalid")

    def test_create(self, sample_aggregate_dict):
        """Test create method."""
        self.mock_scm.post.return_value = sample_aggregate_dict
        create_data = {k: v for k, v in sample_aggregate_dict.items() if k != "id"}
        result = self.client.create(create_data)
        self.mock_scm.post.assert_called_once()
        assert isinstance(result, AggregateInterfaceResponseModel)
        assert result.name == sample_aggregate_dict["name"]

    def test_get(self, sample_aggregate_dict):
        """Test get method."""
        self.mock_scm.get.return_value = sample_aggregate_dict
        result = self.client.get(sample_aggregate_dict["id"])
        assert isinstance(result, AggregateInterfaceResponseModel)
        assert result.id == uuid.UUID(sample_aggregate_dict["id"])

    def test_update(self, sample_aggregate_dict):
        """Test update method."""
        self.mock_scm.put.return_value = sample_aggregate_dict
        update_model = AggregateInterfaceUpdateModel(**sample_aggregate_dict)
        result = self.client.update(update_model)
        self.mock_scm.put.assert_called_once()
        assert isinstance(result, AggregateInterfaceResponseModel)

    def test_delete(self, sample_aggregate_dict):
        """Test delete method."""
        self.client.delete(sample_aggregate_dict["id"])
        expected_endpoint = f"{self.client.ENDPOINT}/{sample_aggregate_dict['id']}"
        self.mock_scm.delete.assert_called_once_with(expected_endpoint)

    def test_list(self, sample_aggregate_dict):
        """Test list method."""
        self.mock_scm.get.return_value = {"data": [sample_aggregate_dict], "limit": 20, "offset": 0, "total": 1}
        result = self.client.list(folder="Test Folder")
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], AggregateInterfaceResponseModel)

    def test_list_with_empty_folder(self):
        """Test list method with empty folder."""
        with pytest.raises(MissingQueryParameterError):
            self.client.list(folder="")

    def test_list_with_missing_container(self):
        """Test list method with missing container."""
        with pytest.raises(InvalidObjectError):
            self.client.list()

    def test_list_filtering_by_mode(self, sample_aggregate_dict):
        """Test list method with mode filtering."""
        iface_l3 = sample_aggregate_dict.copy()
        iface_l3["id"] = str(uuid.uuid4())

        iface_l2 = {
            "id": str(uuid.uuid4()),
            "name": "ae2",
            "folder": "Test Folder",
            "layer2": {"vlan_tag": "100"},
        }

        self.mock_scm.get.return_value = {"data": [iface_l3, iface_l2], "limit": 20, "offset": 0, "total": 2}

        result = self.client.list(folder="Test Folder", mode="layer3")
        assert len(result) == 1
        assert result[0].layer3 is not None

        result = self.client.list(folder="Test Folder", mode="layer2")
        assert len(result) == 1
        assert result[0].layer2 is not None

    def test_fetch(self, sample_aggregate_dict):
        """Test fetch method."""
        self.mock_scm.get.return_value = sample_aggregate_dict
        result = self.client.fetch(name="ae1", folder="Test Folder")
        assert isinstance(result, AggregateInterfaceResponseModel)
        assert result.name == sample_aggregate_dict["name"]

    def test_fetch_with_empty_name(self):
        """Test fetch method with empty name."""
        with pytest.raises(MissingQueryParameterError):
            self.client.fetch(name="", folder="Test Folder")

    def test_fetch_with_missing_container(self):
        """Test fetch method with missing container."""
        with pytest.raises(InvalidObjectError):
            self.client.fetch(name="ae1")

    def test_init_with_negative_max_limit(self):
        """Test initialization with negative max_limit."""
        with pytest.raises(InvalidObjectError) as excinfo:
            AggregateInterface(self.mock_scm, max_limit=-1)
        assert "Invalid max_limit value" in str(excinfo.value)

    def test_init_with_excessive_max_limit(self):
        """Test initialization with excessive max_limit."""
        with pytest.raises(InvalidObjectError) as excinfo:
            client = AggregateInterface(self.mock_scm)
            client.max_limit = 10000
        assert "max_limit exceeds maximum allowed value" in str(excinfo.value)

    def test_max_limit_setter(self):
        """Test max_limit property setter."""
        client = AggregateInterface(self.mock_scm)
        client.max_limit = 1000
        assert client.max_limit == 1000

    def test_list_filtering_by_mode_invalid_type(self, sample_aggregate_dict):
        """Test list method with invalid mode filter type."""
        self.mock_scm.get.return_value = {
            "data": [sample_aggregate_dict],
            "limit": 20,
            "offset": 0,
            "total": 1,
        }
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.list(folder="Test Folder", mode=123)
        assert "Invalid Object" in str(excinfo.value)

    def test_list_response_not_dict(self):
        """Test list method with non-dictionary response."""
        self.mock_scm.get.return_value = ["not", "a", "dictionary"]
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.list(folder="Test Folder")
        assert "Response is not a dictionary" in str(excinfo.value)

    def test_list_response_missing_data_field(self):
        """Test list method with missing data field."""
        self.mock_scm.get.return_value = {"no_data": "field"}
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.list(folder="Test Folder")
        assert '"data" field missing in the response' in str(excinfo.value)

    def test_list_response_data_not_list(self):
        """Test list method with data field not a list."""
        self.mock_scm.get.return_value = {"data": "not a list"}
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.list(folder="Test Folder")
        assert '"data" field must be a list' in str(excinfo.value)

    def test_list_pagination(self, sample_aggregate_dict):
        """Test list method pagination."""
        iface1 = sample_aggregate_dict.copy()
        iface1["id"] = str(uuid.uuid4())
        iface1["name"] = "ae1"

        iface2 = sample_aggregate_dict.copy()
        iface2["id"] = str(uuid.uuid4())
        iface2["name"] = "ae2"

        self.mock_scm.get.side_effect = [
            {"data": [iface1], "limit": 1, "offset": 0, "total": 2},
            {"data": [iface2], "limit": 1, "offset": 1, "total": 2},
            {"data": [], "limit": 1, "offset": 2, "total": 2},
        ]

        self.client.max_limit = 1
        result = self.client.list(folder="Test Folder")

        assert self.mock_scm.get.call_count == 3
        assert len(result) == 2

    def test_list_with_exact_match(self, sample_aggregate_dict):
        """Test list method with exact_match filter."""
        iface1 = sample_aggregate_dict.copy()
        iface1["id"] = str(uuid.uuid4())
        iface1["name"] = "ae1"
        iface1["folder"] = "Folder1"

        iface2 = sample_aggregate_dict.copy()
        iface2["id"] = str(uuid.uuid4())
        iface2["name"] = "ae2"
        iface2["folder"] = "Folder2"

        self.mock_scm.get.return_value = {
            "data": [iface1, iface2],
            "limit": 100,
            "offset": 0,
            "total": 2,
        }

        result = self.client.list(folder="Folder1", exact_match=True)
        assert len(result) == 1
        assert result[0].name == "ae1"

    def test_list_with_exclude_folders(self, sample_aggregate_dict):
        """Test list method with exclude_folders filter."""
        iface1 = sample_aggregate_dict.copy()
        iface1["id"] = str(uuid.uuid4())
        iface1["name"] = "ae1"
        iface1["folder"] = "Folder1"

        iface2 = sample_aggregate_dict.copy()
        iface2["id"] = str(uuid.uuid4())
        iface2["name"] = "ae2"
        iface2["folder"] = "Folder2"

        self.mock_scm.get.return_value = {
            "data": [iface1, iface2],
            "limit": 100,
            "offset": 0,
            "total": 2,
        }

        result = self.client.list(folder="Folder1", exclude_folders=["Folder2"])
        assert len(result) == 1
        assert result[0].name == "ae1"

    def test_list_with_exclude_snippets(self, sample_aggregate_dict):
        """Test list method with exclude_snippets filter."""
        iface1 = sample_aggregate_dict.copy()
        iface1["id"] = str(uuid.uuid4())
        iface1["name"] = "ae1"
        iface1["snippet"] = "Snippet1"
        iface1.pop("folder", None)

        iface2 = sample_aggregate_dict.copy()
        iface2["id"] = str(uuid.uuid4())
        iface2["name"] = "ae2"
        iface2["snippet"] = "Snippet2"
        iface2.pop("folder", None)

        self.mock_scm.get.return_value = {
            "data": [iface1, iface2],
            "limit": 100,
            "offset": 0,
            "total": 2,
        }

        result = self.client.list(snippet="Snippet1", exclude_snippets=["Snippet2"])
        assert len(result) == 1
        assert result[0].name == "ae1"

    def test_list_with_exclude_devices(self, sample_aggregate_dict):
        """Test list method with exclude_devices filter."""
        iface1 = sample_aggregate_dict.copy()
        iface1["id"] = str(uuid.uuid4())
        iface1["name"] = "ae1"
        iface1["device"] = "Device1"
        iface1.pop("folder", None)

        iface2 = sample_aggregate_dict.copy()
        iface2["id"] = str(uuid.uuid4())
        iface2["name"] = "ae2"
        iface2["device"] = "Device2"
        iface2.pop("folder", None)

        self.mock_scm.get.return_value = {
            "data": [iface1, iface2],
            "limit": 100,
            "offset": 0,
            "total": 2,
        }

        result = self.client.list(device="Device1", exclude_devices=["Device2"])
        assert len(result) == 1
        assert result[0].name == "ae1"

    def test_fetch_with_empty_folder(self):
        """Test fetch method with empty folder parameter."""
        with pytest.raises(MissingQueryParameterError) as excinfo:
            self.client.fetch(name="ae1", folder="")
        assert '"folder" is not allowed to be empty' in str(excinfo.value)

    def test_fetch_response_not_dict(self):
        """Test fetch method with non-dictionary response."""
        self.mock_scm.get.return_value = ["not", "a", "dictionary"]
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.fetch(name="ae1", folder="Test Folder")
        assert "Response is not a dictionary" in str(excinfo.value)

    def test_fetch_with_data_array_format(self, sample_aggregate_dict):
        """Test fetch method with data array response format."""
        self.mock_scm.get.return_value = {
            "data": [sample_aggregate_dict],
            "limit": 20,
            "offset": 0,
            "total": 1,
        }

        result = self.client.fetch(name="ae1", folder="Test Folder")
        assert isinstance(result, AggregateInterfaceResponseModel)
        assert result.id == uuid.UUID(sample_aggregate_dict["id"])

    def test_fetch_with_empty_data_array(self):
        """Test fetch method with empty data array."""
        self.mock_scm.get.return_value = {"data": []}
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.fetch(name="ae1", folder="Test Folder")
        assert "No matching aggregate interface found" in str(excinfo.value)

    def test_fetch_with_data_missing_id(self):
        """Test fetch method with data item missing id field."""
        self.mock_scm.get.return_value = {"data": [{"name": "ae1", "folder": "Test Folder"}]}
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.fetch(name="ae1", folder="Test Folder")
        assert "Response data item missing 'id' field" in str(excinfo.value)

    def test_fetch_with_multiple_results(self, sample_aggregate_dict, monkeypatch):
        """Test fetch method with multiple results triggers warning."""
        from unittest.mock import MagicMock

        iface1 = sample_aggregate_dict.copy()
        iface1["id"] = str(uuid.uuid4())
        iface1["name"] = "ae1"

        iface2 = sample_aggregate_dict.copy()
        iface2["id"] = str(uuid.uuid4())
        iface2["name"] = "ae1"

        self.mock_scm.get.return_value = {
            "data": [iface1, iface2],
            "limit": 20,
            "offset": 0,
            "total": 2,
        }

        mock_warning = MagicMock()
        monkeypatch.setattr(self.client.logger, "warning", mock_warning)

        result = self.client.fetch(name="ae1", folder="Test Folder")

        assert isinstance(result, AggregateInterfaceResponseModel)
        assert result.id == uuid.UUID(iface1["id"])
        mock_warning.assert_called_once()
        assert "Multiple aggregate interfaces found" in mock_warning.call_args[0][0]

    def test_fetch_with_invalid_response_structure(self):
        """Test fetch method with invalid response structure."""
        self.mock_scm.get.return_value = {"name": "ae1"}
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.fetch(name="ae1", folder="Test Folder")
        assert "Response has invalid structure" in str(excinfo.value)
