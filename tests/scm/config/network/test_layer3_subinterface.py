"""Unit tests for the Layer3 Subinterface class."""

import uuid
from unittest.mock import MagicMock

import pytest

from scm.config.network.layer3_subinterface import Layer3Subinterface
from scm.exceptions import InvalidObjectError, MissingQueryParameterError
from scm.models.network.layer3_subinterface import (
    Layer3SubinterfaceResponseModel,
    Layer3SubinterfaceUpdateModel,
)


@pytest.fixture
def sample_layer3_dict():
    """Return a sample layer3 subinterface dictionary."""
    return {
        "id": str(uuid.uuid4()),
        "name": "ethernet1/1.100",
        "tag": 100,
        "folder": "Test Folder",
        "parent_interface": "ethernet1/1",
        "comment": "Test layer3 subinterface",
        "mtu": 1500,
        "ip": [{"name": "192.168.1.1/24"}],
    }


@pytest.mark.usefixtures("load_env")
class TestLayer3SubinterfaceBase:
    """Base class for Layer3Subinterface tests."""

    @pytest.fixture(autouse=True)
    def setup_method(self, mock_scm):
        """Setup method that runs before each test."""
        self.mock_scm = mock_scm
        self.mock_scm.get = MagicMock()
        self.mock_scm.post = MagicMock()
        self.mock_scm.put = MagicMock()
        self.mock_scm.delete = MagicMock()
        self.client = Layer3Subinterface(self.mock_scm, max_limit=5000)


class TestLayer3Subinterface(TestLayer3SubinterfaceBase):
    """Test suite for Layer3Subinterface class."""

    def test_init(self):
        """Test initialization of Layer3Subinterface class."""
        client = Layer3Subinterface(self.mock_scm)
        assert client.ENDPOINT == "/config/network/v1/layer3-subinterfaces"
        assert client.max_limit == client.DEFAULT_MAX_LIMIT

    def test_init_with_invalid_max_limit(self):
        """Test initialization with invalid max_limit."""
        with pytest.raises(InvalidObjectError):
            Layer3Subinterface(self.mock_scm, max_limit="invalid")

    def test_create(self, sample_layer3_dict):
        """Test create method."""
        self.mock_scm.post.return_value = sample_layer3_dict
        create_data = {k: v for k, v in sample_layer3_dict.items() if k != "id"}
        result = self.client.create(create_data)
        self.mock_scm.post.assert_called_once()
        assert isinstance(result, Layer3SubinterfaceResponseModel)
        assert result.name == sample_layer3_dict["name"]

    def test_get(self, sample_layer3_dict):
        """Test get method."""
        self.mock_scm.get.return_value = sample_layer3_dict
        result = self.client.get(sample_layer3_dict["id"])
        assert isinstance(result, Layer3SubinterfaceResponseModel)
        assert result.id == uuid.UUID(sample_layer3_dict["id"])

    def test_update(self, sample_layer3_dict):
        """Test update method."""
        self.mock_scm.put.return_value = sample_layer3_dict
        update_model = Layer3SubinterfaceUpdateModel(**sample_layer3_dict)
        result = self.client.update(update_model)
        self.mock_scm.put.assert_called_once()
        assert isinstance(result, Layer3SubinterfaceResponseModel)

    def test_delete(self, sample_layer3_dict):
        """Test delete method."""
        self.client.delete(sample_layer3_dict["id"])
        expected_endpoint = f"{self.client.ENDPOINT}/{sample_layer3_dict['id']}"
        self.mock_scm.delete.assert_called_once_with(expected_endpoint)

    def test_list(self, sample_layer3_dict):
        """Test list method."""
        self.mock_scm.get.return_value = {"data": [sample_layer3_dict], "limit": 20, "offset": 0, "total": 1}
        result = self.client.list(folder="Test Folder")
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], Layer3SubinterfaceResponseModel)

    def test_list_with_empty_folder(self):
        """Test list method with empty folder."""
        with pytest.raises(MissingQueryParameterError):
            self.client.list(folder="")

    def test_list_with_missing_container(self):
        """Test list method with missing container."""
        with pytest.raises(InvalidObjectError):
            self.client.list()

    def test_list_filtering(self, sample_layer3_dict):
        """Test list method with filtering."""
        iface1 = sample_layer3_dict.copy()
        iface1["id"] = str(uuid.uuid4())
        iface1["tag"] = 100
        iface1["mtu"] = 1500
        iface2 = sample_layer3_dict.copy()
        iface2["id"] = str(uuid.uuid4())
        iface2["tag"] = 200
        iface2["mtu"] = 9000

        self.mock_scm.get.return_value = {"data": [iface1, iface2], "limit": 20, "offset": 0, "total": 2}

        result = self.client.list(folder="Test Folder", tag=100)
        assert len(result) == 1
        assert result[0].tag == 100

        result = self.client.list(folder="Test Folder", mtu=9000)
        assert len(result) == 1
        assert result[0].mtu == 9000

    def test_fetch(self, sample_layer3_dict):
        """Test fetch method."""
        self.mock_scm.get.return_value = sample_layer3_dict
        result = self.client.fetch(name="ethernet1/1.100", folder="Test Folder")
        assert isinstance(result, Layer3SubinterfaceResponseModel)
        assert result.name == sample_layer3_dict["name"]

    def test_fetch_with_empty_name(self):
        """Test fetch method with empty name."""
        with pytest.raises(MissingQueryParameterError):
            self.client.fetch(name="", folder="Test Folder")

    def test_fetch_with_missing_container(self):
        """Test fetch method with missing container."""
        with pytest.raises(InvalidObjectError):
            self.client.fetch(name="ethernet1/1.100")
