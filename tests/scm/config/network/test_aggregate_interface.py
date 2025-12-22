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
